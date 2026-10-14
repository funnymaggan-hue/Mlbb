from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_db
from app.api.deps import current_telegram_user
from app.config import settings
from app.models.entities import User, PlayerProfile, PlayerVerification, Team, TeamMember, Tournament, TournamentRegistration, AdminAuditLog, Announcement
from app.schemas.api import PlayerSubmit, TournamentCreate, TeamCreate
from app.services.player_verification import validate_format, query_provider
router = APIRouter(prefix="/api")
def is_admin(tg_id: int) -> bool: return tg_id in settings.admin_ids
async def get_or_create_user(db: AsyncSession, tg: dict) -> User:
    result = await db.execute(select(User).where(User.telegram_id == int(tg["id"])))
    user = result.scalar_one_or_none()
    if user is None:
        user = User(telegram_id=int(tg["id"]), username=tg.get("username"), display_name=(tg.get("first_name") or "Player")[:120])
        db.add(user); await db.flush()
    return user
@router.get("/me")
async def me(tg=Depends(current_telegram_user), db: AsyncSession=Depends(get_db)):
    user = await get_or_create_user(db, tg)
    profile = (await db.execute(select(PlayerProfile).where(PlayerProfile.user_id == user.id))).scalar_one_or_none()
    await db.commit()
    return {"telegram_id": user.telegram_id, "display_name": user.display_name, "language": user.language, "is_admin": is_admin(user.telegram_id), "profile": None if not profile else {"mlbb_id":profile.mlbb_id,"server_id":profile.server_id,"nickname":profile.nickname,"verification_status":profile.verification_status}}
@router.put("/language/{language}")
async def set_language(language: str, tg=Depends(current_telegram_user), db: AsyncSession=Depends(get_db)):
    if language not in {"uz","ru","en"}: raise HTTPException(400, "Til qo‘llab-quvvatlanmaydi")
    user=await get_or_create_user(db,tg); user.language=language; await db.commit()
    return {"language":language}
@router.post("/player/verify")
async def submit_player(payload: PlayerSubmit, tg=Depends(current_telegram_user), db: AsyncSession=Depends(get_db)):
    user=await get_or_create_user(db,tg)
    if not validate_format(payload.mlbb_id, payload.server_id):
        row=PlayerVerification(user_id=user.id, mlbb_id=payload.mlbb_id[:20], server_id=payload.server_id[:10], submitted_nickname=payload.nickname, status="invalid_format")
        db.add(row); await db.commit()
        raise HTTPException(422, detail={"status":"invalid_format","message":"MLBB ID yoki server ID formati noto‘g‘ri"})
    result=await query_provider(payload.mlbb_id, payload.server_id)
    status=result["status"]
    if status == "verified" and result.get("nickname","").casefold() != payload.nickname.strip().casefold():
        status="pending_review"
    if status in {"unverified","provider_error"}: status="pending_review"
    row=PlayerVerification(user_id=user.id,mlbb_id=payload.mlbb_id,server_id=payload.server_id,submitted_nickname=payload.nickname,status=status,provider_name=result.get("provider"),provider_response=result.get("reason"))
    db.add(row)
    profile=(await db.execute(select(PlayerProfile).where(PlayerProfile.user_id==user.id))).scalar_one_or_none()
    if profile is None:
        profile=PlayerProfile(user_id=user.id,mlbb_id=payload.mlbb_id,server_id=payload.server_id,nickname=payload.nickname,role=payload.role,verification_status=status); db.add(profile)
    else:
        profile.mlbb_id=payload.mlbb_id; profile.server_id=payload.server_id; profile.nickname=payload.nickname; profile.role=payload.role; profile.verification_status=status
    await db.commit()
    return {"status":status,"message":result.get("reason","Natija administrator ko‘rigiga yuborildi"),"verification_id":row.id}
@router.get("/tournaments")
async def tournaments(db: AsyncSession=Depends(get_db)):
    rows=(await db.execute(select(Tournament).order_by(Tournament.created_at.desc()))).scalars().all()
    output=[]
    for t in rows:
        count=(await db.execute(select(func.count()).select_from(TournamentRegistration).where(TournamentRegistration.tournament_id==t.id,TournamentRegistration.status!="rejected"))).scalar_one()
        output.append({"id":t.id,"title":t.title,"description":t.description,"mode":t.mode,"prize_pool":t.prize_pool,"max_teams":t.max_teams,"registered_teams":count,"status":t.status,"starts_at":t.starts_at.isoformat() if t.starts_at else None})
    return output
@router.post("/teams")
async def create_team(payload: TeamCreate, tg=Depends(current_telegram_user), db: AsyncSession=Depends(get_db)):
    user=await get_or_create_user(db,tg)
    existing=(await db.execute(select(TeamMember).where(TeamMember.user_id==user.id,TeamMember.status=="active"))).scalar_one_or_none()
    if existing: raise HTTPException(409,"Siz allaqachon jamoa a’zosisiz")
    team=Team(name=payload.name.strip(),captain_user_id=user.id); db.add(team)
    try:
        await db.flush(); db.add(TeamMember(team_id=team.id,user_id=user.id,role="captain")); await db.commit()
    except Exception:
        await db.rollback(); raise HTTPException(409,"Jamoa nomi band yoki a’zolik cheklovi buzildi")
    return {"id":team.id,"name":team.name}
@router.post("/tournaments/{tournament_id}/register")
async def register_team(tournament_id: int, tg=Depends(current_telegram_user), db: AsyncSession=Depends(get_db)):
    user=await get_or_create_user(db,tg)
    membership=(await db.execute(select(TeamMember).where(TeamMember.user_id==user.id,TeamMember.status=="active",TeamMember.role=="captain"))).scalar_one_or_none()
    if not membership: raise HTTPException(400,"Faqat jamoa sardori ro‘yxatdan o‘tkaza oladi")
    t=(await db.execute(select(Tournament).where(Tournament.id==tournament_id))).scalar_one_or_none()
    if not t: raise HTTPException(404,"Turnir topilmadi")
    if t.status!="open": raise HTTPException(409,"Turnir ro‘yxatdan o‘tish uchun ochiq emas")
    count=(await db.execute(select(func.count()).select_from(TournamentRegistration).where(TournamentRegistration.tournament_id==t.id,TournamentRegistration.status!="rejected"))).scalar_one()
    if count>=t.max_teams: raise HTTPException(409,"Turnirda bo‘sh joy qolmagan")
    row=TournamentRegistration(tournament_id=t.id,team_id=membership.team_id,registered_by=user.id,status="pending"); db.add(row)
    try: await db.commit()
    except Exception: await db.rollback(); raise HTTPException(409,"Bu jamoa allaqachon ariza yuborgan")
    return {"registration_id":row.id,"status":row.status}
@router.post("/admin/tournaments")
async def create_tournament(payload: TournamentCreate, tg=Depends(current_telegram_user), db: AsyncSession=Depends(get_db)):
    if not is_admin(int(tg["id"])): raise HTTPException(403,"Administrator ruxsati kerak")
    if payload.status not in {"draft","open","full","live","finished","cancelled"}: raise HTTPException(422,"Noto‘g‘ri turnir holati")
    t=Tournament(**payload.model_dump(),created_by=int(tg["id"])); db.add(t); await db.flush()
    db.add(AdminAuditLog(admin_telegram_id=int(tg["id"]),action="tournament.create",entity_type="tournament",entity_id=t.id,details=t.title))
    await db.commit(); return {"id":t.id,"title":t.title,"status":t.status}
@router.post("/admin/verifications/{verification_id}/{decision}")
async def review_verification(verification_id:int, decision:str, tg=Depends(current_telegram_user), db: AsyncSession=Depends(get_db)):
    if not is_admin(int(tg["id"])): raise HTTPException(403,"Administrator ruxsati kerak")
    if decision not in {"approve","reject","pending"}: raise HTTPException(422,"Noto‘g‘ri qaror")
    row=(await db.execute(select(PlayerVerification).where(PlayerVerification.id==verification_id))).scalar_one_or_none()
    if not row: raise HTTPException(404,"Ariza topilmadi")
    # Manual approval is explicitly labeled as an admin decision, not provider verification.
    row.status="pending_review" if decision=="pending" else ("manual_approved" if decision=="approve" else "rejected")
    row.reviewed_by=int(tg["id"]); row.review_note="Manual admin review; this is not provider verification"
    profile=(await db.execute(select(PlayerProfile).where(PlayerProfile.user_id==row.user_id))).scalar_one_or_none()
    if profile: profile.verification_status=row.status
    db.add(AdminAuditLog(admin_telegram_id=int(tg["id"]),action=f"verification.{decision}",entity_type="player_verification",entity_id=row.id))
    await db.commit(); return {"id":row.id,"status":row.status,"reviewed_by":int(tg["id"])}
@router.get("/admin/verifications")
async def pending_verifications(tg=Depends(current_telegram_user), db: AsyncSession=Depends(get_db)):
    if not is_admin(int(tg["id"])): raise HTTPException(403,"Administrator ruxsati kerak")
    rows=(await db.execute(select(PlayerVerification).where(PlayerVerification.status.in_(["pending_review","unverified","provider_error","invalid_format"])).order_by(PlayerVerification.created_at))).scalars().all()
    return [{"id":r.id,"user_id":r.user_id,"mlbb_id":r.mlbb_id,"server_id":r.server_id,"nickname":r.submitted_nickname,"status":r.status} for r in rows]
@router.get("/announcements")
async def announcements(db: AsyncSession=Depends(get_db)):
    rows=(await db.execute(select(Announcement).where(Announcement.active==True))).scalars().all()
    return [{"title":a.title,"body":a.body,"banner_url":a.banner_url,"target_url":a.target_url} for a in rows]
