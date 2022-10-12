from fastapi import APIRouter
from fastapi import Request,Depends
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from typing import Optional

from db.repository.jobs import list_jobs, retreive_job, delete_job_by_id, search_job
from db.session import get_db

from db.models.users import User  
from apis.version1.route_login import get_current_user_from_token
from webapp.jobs.forms import JobCreateForm
from schemas.jobs import JobCreate
from db.repository.jobs import create_new_job
from fastapi import responses, status
from fastapi.security.utils import get_authorization_scheme_param


templates = Jinja2Templates(directory="templates")
router = APIRouter(include_in_schema=False)

@router.get("/post-a-job/")
def create_job(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse("jobs/create_job.html", {"request": request})


@router.post("/post-a-job/")
async def create_job(request: Request, db: Session = Depends(get_db)):
    form = JobCreateForm(request)
    await form.load_data()
    if form.is_valid():
        try:
            token = request.cookies.get("access_token")
            scheme, param = get_authorization_scheme_param(
                token
            )
            current_user: User = get_current_user_from_token(token=param, db=db)
            job = JobCreate(**form.__dict__)
            job = create_new_job(job=job, db=db, owner_id=current_user.id)
            return responses.RedirectResponse(
                f"/jobs/detail/{job.id}", status_code=status.HTTP_302_FOUND
            )
        except Exception as e:
            form.__dict__.get("errors").append(
                "You might not be logged in, In case problem persists please contact us."
            )
            return templates.TemplateResponse("jobs/create_job.html", form.__dict__)
    return templates.TemplateResponse("jobs/create_job.html", form.__dict__)


@router.get("/")
async def home(request: Request,db: Session = Depends(get_db), msg:str = None):
    jobs = list_jobs(db=db)
    return templates.TemplateResponse(
        "general_pages/homepage.html", {"request": request,"jobs":jobs,"msg":msg}
    )


@router.get("/jobs/detail/{id}")
async def job_detail(id:int,request: Request, db:Session = Depends(get_db)):
    job = retreive_job(id=id, db=db)
    return templates.TemplateResponse(
        "jobs/detail.html", {"request": request,"job":job}
    )
    
    
@router.get("/delete-job/")
def show_jobs_to_delete(request: Request, db: Session = Depends(get_db)):
    jobs = list_jobs(db=db)
    return templates.TemplateResponse(
        "jobs/show_jobs_to_delete.html", {"request": request, "jobs": jobs}
    )


@router.get("/jobs/delete/{id}")
def job_delete(id: int,request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    scheme, param = get_authorization_scheme_param(token)
    current_user: User = get_current_user_from_token(token=param, db=db)
    delete_job_by_id(id=id, db=db, owner_id=current_user.id)
    jobs = list_jobs(db=db)
    return templates.TemplateResponse("jobs/show_jobs_to_delete.html", {"request": request, "jobs": jobs})


@router.get("/search/")
def search(request: Request, db: Session = Depends(get_db), query: Optional[str] = None):
    jobs = search_job(query, db=db)
    return templates.TemplateResponse("general_pages/homepage.html", {"request": request, "jobs": jobs})    