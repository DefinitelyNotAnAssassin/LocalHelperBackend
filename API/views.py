from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.contrib.auth import authenticate, login as login_user, logout as logout_user
from Models.models import Job, JobApplication, Company, Account, UserResume
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated 
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import make_password
# permission_classes 

import json


def jobs(request):
    jobs = Job.objects.all()
    return JsonResponse({"jobs": list(jobs.values())})

@api_view(['GET'])
def job(request, id):
    try:
        job = Job.objects.get(id=id)
        job_data = {
            "id": job.id,
            "title": job.title,
            "description": job.description,
            "address": job.address,
            "salary": job.salary,
            "company_id": job.company_id,
            "owner_id": job.owner_id,
            "created_at": job.created_at,
            "status": job.status,
            "slots": job.slots,
            "thumbnail": job.thumbnail.url if job.thumbnail else None
        }
        return JsonResponse({"job": job_data})
    except Job.DoesNotExist:
        return JsonResponse({"error": "Job not found"}, status=404)

@csrf_exempt    
def login(request):
    if request.method == "POST":
        data = request.body.decode('utf-8')
        data = json.loads(data)
        email = data.get('email')
        password = data.get('password')
        print(email, password)
        user = authenticate(request, username=email, password=password)
        
       
        if user:
            login_user(request, user)
            refresh = RefreshToken.for_user(user) 
            return JsonResponse({"message": "Logged in", "refresh": str(refresh), "access": str(refresh.access_token), "user": {"email": user.email, "first_name": user.first_name, "last_name": user.last_name, "role": user.account_type}})         
        else:
            return HttpResponse("Invalid credentials", status=401)  
    return  HttpResponse("Invalid request", status=400)


@csrf_exempt 
def signup(request):
    if request.method == "POST":
        account_type = request.GET.get('type')
        if account_type == "employee": 
            data = request.body.decode('utf-8') 
            data = json.loads(data) 
            print("employee")
            print(data)
            password = data.get('password')
            data['password'] = make_password(password)
            user = Account.objects.create_user(
                username=data.get('email'),
                email=data.get('email'),
                password=data.get('password'),
                account_type="Employee",
                first_name=data.get('firstName'),
                last_name=data.get('lastName'),
                date_of_birth=data.get('birthDate'),
                sex=data.get('sex'),
                address=data.get('address'),
                contact_number=data.get('contactNo')
            )
            
            # create a resume for the user 
         
        elif account_type == "employer": 
            user = Account.objects.create_user(username=data.get('email'), email=data.get('email'), password=data.get('password'), account_type="Employer")
            user.first_name = data.get('company_name')
        else:
            return JsonResponse({"status" : 401,"message": "Invalid account type"})
      
        user.save()
        resume = UserResume(user=user, experience="", skills="", education="")
        resume.save()
        access_token = RefreshToken.for_user(user)  
        return JsonResponse({"message": "Account created successfully", "access": str(access_token.access_token), "refresh": str(access_token)})
        
        
        
        
@api_view(['POST'])
@csrf_exempt
def refresh_token(request):
    if request.method == "POST":
        data = request.body.decode('utf-8')
        data = json.loads(data)
        refresh = data.get('refresh')
        token = RefreshToken(refresh)
        user = token.user
        access = str(token.access_token)
        return JsonResponse({"access": access})
    return HttpResponse("Invalid request", status=400)
        
        
        
        
  
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def verify_auth(request):
    print(request.user)
    if request.user.is_authenticated: 
        user = { 
            "id": request.user.id, 
            "username": request.user.username, 
            "first_name": request.user.first_name,
            "last_name": request.user.last_name,
            "email": request.user.email, 
            "date_of_birth": request.user.date_of_birth, 
            "role": request.user.account_type,
            "contact_number": request.user.contact_number, 
            "address": request.user.address,
            
        }
        return JsonResponse(user, safe=False) 
    else:
        return JsonResponse({"error": "User not authenticated"}, status=400) 
          
        
        
@api_view(['POST']) 
@permission_classes([IsAuthenticated])
def apply_job(request, id):
    if request.method == "POST":
        job = Job.objects.get(id=id)
        application = JobApplication(job=job, applicant=request.user)
        application.save()
        # remove one slot from the job 
        job.slots -= 1 
        job.save() 
        # remove the job from saved jobs 
        request.user.saved_jobs.remove(job)
        return JsonResponse({"message": "Application submitted successfully"})
    return JsonResponse({"error": "Invalid request"}, status=400)        


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def save_job(request, id):
    if request.method == "POST":
        job = Job.objects.get(id=id)
        request.user.saved_jobs.add(job)
        return JsonResponse({"message": "Job saved successfully"})
    return JsonResponse({"error": "Invalid request"}, status=400)




@api_view(['GET'])
@permission_classes([IsAuthenticated])
def saved_jobs(request):
    print(request.user)
    jobs = request.user.saved_jobs.all()
    return JsonResponse({"jobs": list(jobs.values())})



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def jobs_applied(request):
    job_applications = JobApplication.objects.filter(applicant=request.user)
    jobs = []
    for application in job_applications:
        job = application.job
        job_data = {
            "id": job.id,
            "title": job.title,
            "description": job.description,
            "address": job.address,
            "salary": job.salary,
            "company_id": job.company_id,
            "owner_id": job.owner_id,
            "created_at": job.created_at,
            "status": application.status,
            "slots": job.slots,
            "thumbnail": job.thumbnail.url if job.thumbnail else None,
            "application_date": application.created_at,
            "application_status": application.status
        }
        jobs.append(job_data)
    return JsonResponse({"jobs": jobs})


@api_view(['POST'])
def create_job(request):
    if request.method == "POST":
        data = request.body.decode('utf-8')
        data = json.loads(data)
        company = Company.objects.get(owner=request.user) 
        job = Job(
            title=data.get('jobPosition'),
            description=data.get('jobDescription'),
            address=company.address,    
            salary=data.get('salary'),
            company=company,
            owner=request.user,
            job_type=data.get('jobType'),
            requirements=data.get('jobRequirements'), 
            slots=data.get('slots'),    
            thumbnail=company.logo
        )
        job.save()
        return JsonResponse({"message": "Job created successfully", "job_id": job.id})
    return JsonResponse({"error": "Invalid request"}, status=400)



@api_view(['GET'])   
@permission_classes([IsAuthenticated])
def jobs_created(request):
    jobs = Job.objects.filter(owner=request.user)
    print(jobs)
    return JsonResponse({"jobs": list(jobs.values())})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def job_applications(request):
    if request.user.account_type == "Employer":
        applications = JobApplication.objects.filter(job__owner=request.user)
        applications_data = []
        for application in applications:
            application_data = {
                "id": application.id,
                "job_id": application.job_id,
                "applicant_id": application.applicant_id,
                "created_at": application.created_at,
                "status": application.status
            }
            applications_data.append(application_data)
        return JsonResponse({"applications": applications_data})
    return JsonResponse({"error": "Unauthorized"}, status=401)

def job_application(request, id):
    job = Job.objects.get(id=id)
    application = JobApplication.objects.filter(job=job).all()
    application_data = []   
    for app in application:
        application_data.append({
            "id": app.id,
            "applicant_id": app.applicant.id,   
            "applicant": app.applicant.username,
            'first_name': app.applicant.first_name, 
            'last_name': app.applicant.last_name,
            "status": app.status,
            "created_at": app.created_at
        })
        
    
    job_data = { 
                "title": job.title,
                "description": job.description,
                "job_id": job.id,
                }
    print(application_data)
    return JsonResponse({"application": application_data, "job": job_data})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def accept_application(request, id):
    if request.method == "POST":
        application = JobApplication.objects.get(id=id)
        application.status = "Accepted"
        application.save()
        return JsonResponse({"message": "Application accepted"})
    return JsonResponse({"error": "Invalid request"}, status=400)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reject_application(request, id):
    if request.method == "POST":
        application = JobApplication.objects.get(id=id)
        application.status = "Rejected"
        application.save()
        return JsonResponse({"message": "Application rejected"})
    return JsonResponse({"error": "Invalid request"}, status=400)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def save_resume(request):
    if request.method == "POST":
        data = request.body.decode('utf-8')
        data = json.loads(data)
        try:
            resume = UserResume.objects.get(user=request.user)
            resume.experience = data.get('experience')
            resume.skills = data.get('skills')
            resume.education = data.get('education')
            resume.save()
            return JsonResponse({"message": "Resume updated successfully"})
        except UserResume.DoesNotExist:
            resume = UserResume(
                user=request.user,
                experience=data.get('experience'),
                skills=data.get('skills'),
                education=data.get('education')
            )
            resume.save()
            return JsonResponse({"message": "Resume created successfully"})
    return JsonResponse({"error": "Invalid request"}, status=400)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_resume(request):
    try:
        resume = UserResume.objects.get(user=request.user)
        resume_data = {
            "experience": resume.experience,
            "skills": resume.skills,
            "education": resume.education
        }
        return JsonResponse(resume_data)
    except UserResume.DoesNotExist:
        return JsonResponse({"error": "Resume not found"}, status=404)
    
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def applicant_resume(request, id):
    try:
        user = Account.objects.get(id=id)
        print(user)
        resume = UserResume.objects.get(user=user)
        resume_data = {
            "experience": resume.experience,
            "skills": resume.skills,
            "education": resume.education
        }
        return JsonResponse(resume_data)
    except UserResume.DoesNotExist:
        return JsonResponse({"error": "Resume not found"}, status=404)
    except Account.DoesNotExist:    
        return JsonResponse({"error": "User not found"}, status=404)
    
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_status(request, id):
    if request.method == "POST":
        application = JobApplication.objects.get(id=id)
        data = request.body.decode('utf-8')
        data = json.loads(data)
        status = data.get('status')
        application.status = status
        application.save()
        return JsonResponse({"message": "Status updated successfully"})
    return JsonResponse({"error": "Invalid request"}, status=400)
    
    
    
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def close_job(request):
    if request.method == "POST":
        data = request.body.decode('utf-8')
        data = json.loads(data)
        job_id = data.get('jobId')
        job = Job.objects.get(id=job_id)
        job.status = "closed"
        job.save()
        return JsonResponse({"message": "Job closed successfully"})
    return JsonResponse({"error": "Invalid request"}, status=400)

