from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.contrib.auth import authenticate, login as login_user, logout as logout_user
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from django.db.models import Count
from Models.models import Job, JobApplication, Company, Account, UserResume
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated 

import datetime
import json
import random


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
        print(data)
        email = data.get('email')
        password = data.get('password')
        print(email, password)
        user = Account.objects.get(email=email)        
        checkpass = user.check_password(password) 
        if checkpass:
            if user.isVerified: 
                login_user(request, user)
                
                refresh = RefreshToken.for_user(user) 
                return JsonResponse({"message": "Logged in", "refresh": str(refresh), "access": str(refresh.access_token), "user": {"email": user.email, "first_name": user.first_name, "last_name": user.last_name, "role": user.account_type}}) 
            else: 
                return JsonResponse({"message": "Account not verified"}, status=401)        
        else:
            return HttpResponse("Invalid credentials", status=402)  
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
            user = Account.objects.create_user(
                username=data.get('email'),
                email=data.get('email'),
                password=password,
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
            data = request.POST
            files = request.FILES 
            
            print(data)
            user = Account.objects.create_user(username=data.get('email'), email=data.get('email'), password=data.get('password'), account_type="Employer")
            user.first_name = data.get('company_name')
            # The code snippet appears to be creating an instance of a `Company` class with the
            # `owner` attribute set to a variable `user` and the `name` attribute set to a variable
            # `dat`. However, the code is incomplete and contains syntax errors.
            
            company = Company(owner=user, name=data.get('company_name'),  address=data.get('companyAddress'), logo=files.get('logo')) 
            company.save()
        else:
            return JsonResponse({"status" : 401,"message": "Invalid account type"})

        otp = str(random.randint(100000, 999999))    
        send_mail(
            'Verify your account',
            f'Your OTP is {otp}. Please verify your account by clicking the following link: http://localhost:5173/verifyEmail?email={user.email}&otp={otp}',
            'no-reply@example.com',
            [user.email],
        )
        user.otp = otp  
        user.save()
        resume = UserResume(user=user, experience="", skills="", education="", reason = "")
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
        # Check if user has a resume with content
        try:
            resume = UserResume.objects.get(user=request.user)
            if not resume.experience or not resume.skills or not resume.education or not resume.reason:
                return JsonResponse({"error": "Please complete your resume before applying"}, status=400)
        except UserResume.DoesNotExist:
            return JsonResponse({"error": "Please create a resume before applying"}, status=400)

        job = Job.objects.get(id=id)
        application = JobApplication(job=job, applicant=request.user)
        application.save()
        job.slots -= 1 
        job.save() 
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
        print(data)
        try:
            resume = UserResume.objects.get(user=request.user)
            resume.experience = data.get('experience')
            resume.skills = data.get('skills')
            resume.education = data.get('education')
            resume.reason = data.get('reason')
            resume.save()
            return JsonResponse({"message": "Resume updated successfully"})
        except UserResume.DoesNotExist:
            resume = UserResume(
                user=request.user,
                experience=data.get('experience'),
                skills=data.get('skills'),
                education=data.get('education'),
                reason = data.get('reason')
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
            "education": resume.education, 
            "reason": resume.reason
            
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
            "education": resume.education, 
            "reason": resume.reason 
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

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def save_profile(request):
    if request.method == "POST":
        data = request.body.decode('utf-8')
        data = json.loads(data)
        print(data)
        user = request.user
        user.first_name = data.get('firstName')
        user.last_name = data.get('lastName')
        user.email = data.get('email')
        user.date_of_birth = data.get('birthDate')
        user.social_media = data.get('socialMedia')  
        user.save()
        return JsonResponse({"message": "Profile updated successfully"})
      

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_dashboard(request):
    if request.user.account_type == "Admin":
        jobs = Job.objects.all()
        job_applications = JobApplication.objects.all()
        companies = Company.objects.all()
        users = Account.objects.all()

        # Calculate age groups
        from django.db.models import F, ExpressionWrapper, fields
        from datetime import date

        age_groups = users.annotate(
            age=ExpressionWrapper(
                date.today().year - F('date_of_birth__year'),
                output_field=fields.IntegerField()
            )
        ).values('age').annotate(count=Count('id')).order_by('age')

        # Calculate total applications today and this month
        today = datetime.date.today()
        total_applications_today = job_applications.filter(created_at__date=today).count()
        total_applications_this_month = job_applications.filter(created_at__year=today.year, created_at__month=today.month).count()

        # Get job seekers
        job_seekers = users.filter(account_type="Employee").values('id', 'first_name', 'last_name', 'email', 'date_of_birth')

        # Get companies
        companies_data = companies.values('id', 'name')

    
        return JsonResponse({
            "jobs": jobs.count(),
            "job_applications": job_applications.count(),
            "companies": companies.count(),
            "users": users.count(),
            "ageGroups": list(age_groups),
            "totalApplicationsToday": total_applications_today,
            "totalApplicationsThisMonth": total_applications_this_month,
            "jobSeekers": list(job_seekers),
            "companies": list(companies_data)
        })
    return JsonResponse({"error": "Unauthorized"}, status=401)





def applicant_contact(request, applicantId):
    try:
        applicant = Account.objects.get(id=applicantId)
        return JsonResponse({"name": applicant.first_name + ' ' + applicant.last_name, "email": applicant.email, "phone": applicant.contact_number, "social_media": applicant.social_media})
    except Account.DoesNotExist:
        return JsonResponse({"error": "User not found"}, status=404)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_job(request, id):
    try:
        job = Job.objects.get(id=id, owner=request.user)
        data = json.loads(request.body.decode('utf-8'))
        job.title = data.get('title', job.title)
        job.description = data.get('description', job.description)
        job.status = data.get('status', job.status)
        job.slots = data.get('slots', job.slots)
        job.job_type = data.get('job_type', job.job_type)
        job.requirements = data.get('requirements', job.requirements)
        job.save()
        return JsonResponse({"message": "Job updated successfully"})
    except Job.DoesNotExist:
        return JsonResponse({"error": "Job not found"}, status=404)

@csrf_exempt
def verify_email(request):
    if request.method == "POST":
        data = json.loads(request.body)
        email = data.get('email')
        otp = data.get('otp')
        
        try:
            user = Account.objects.get(email=email)
            if user.otp == otp:
                user.isVerified = True
                user.otp = 0  # Clear OTP after verification
                user.save()
                
                # Login the user
                login_user(request, user)
                
                # Generate tokens
                refresh = RefreshToken.for_user(user)
                return JsonResponse({
                    "message": "Email verified successfully",
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                    "user": {
                        "email": user.email,
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                        "role": user.account_type
                    }
                })
            else:
                return JsonResponse({"error": "Invalid OTP"}, status=400)
        except Account.DoesNotExist:
            return JsonResponse({"error": "User not found"}, status=404)
            
    return JsonResponse({"error": "Invalid request"}, status=400)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def remove_saved_job(request, id):
    if request.method == "POST":
        try:
            job = Job.objects.get(id=id)
            request.user.saved_jobs.remove(job)
            return JsonResponse({"message": "Job removed from saved jobs successfully"})
        except Job.DoesNotExist:
            return JsonResponse({"error": "Job not found"}, status=404)
    return JsonResponse({"error": "Invalid request"}, status=400)