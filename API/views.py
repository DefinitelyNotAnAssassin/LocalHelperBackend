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
    jobs = Job.objects.select_related('company', 'owner').all()
    jobs_list = []
    for job in jobs:
        job_data = {
            'id': job.id,
            'title': job.title,
            'job_type': job.job_type,   
            'requirements': job.requirements,
            'description': job.description,
            'address': job.address,
            'salary': job.salary,
            'salary_type': job.salary_type,
            'status': job.status,
            'slots': job.slots,
            'thumbnail': job.thumbnail.url if job.thumbnail else None,
            'company': {
                'name': job.company.name,
                'address': job.company.address,
                'logo': job.company.logo.url if job.company.logo else None,
            },
            'employer': {
                'name': job.owner.first_name,
                'email': job.owner.email,
            }
        }
        jobs_list.append(job_data)
    return JsonResponse({"jobs": jobs_list})

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
            "job_type": job.job_type,   
            "requirements": job.requirements,
            "salary_type": job.salary_type,
            "company_id": job.company_id,
            "company" : { 
                "name": job.company.name,
                "address": job.company.address,
                "logo": job.company.logo.url if job.company.logo else None
                },
            
            "owner_id": job.owner_id,
            "employer": {   
                "name": job.owner.first_name,
                "email": job.owner.email,
                "contact_number": job.owner.contact_number, 
            },
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
            print(files)
            user = Account.objects.create_user(username=data.get('email'), email=data.get('email'), password=data.get('password'), account_type="Employer")
            user.first_name = data.get('company_name')
            
            company = Company(owner=user, name=data.get('company_name'), address=data.get('companyAddress'), logo=files.get('companyLogo'))
            company.save()
        else:
            return JsonResponse({"status" : 401,"message": "Invalid account type"})

        otp = str(random.randint(100000, 999999))    
        send_mail(
            'Verify your account',
            f'Your OTP is {otp}. Please verify your account by clicking the following link: https://localhelper.vercel.app/verifyEmail?email={user.email}&otp={otp}',
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

        # Check if user has already applied for the job
        if JobApplication.objects.filter(job_id=id, applicant=request.user).exists():
            return JsonResponse({"error": "You have already applied for this job"}, status=400)

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
    jobs_list = list(jobs.values())
    for job in jobs_list:
        job['salary_type'] = Job.objects.get(id=job['id']).salary_type
    return JsonResponse({"jobs": jobs_list})



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
            "salary_type": job.salary_type,
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
            salary_type=data.get('salaryType'),  # Add salary_type
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
    jobs_list = list(jobs.values())
    for job in jobs_list:
        job['salary_type'] = Job.objects.get(id=job['id']).salary_type
    return JsonResponse({"jobs": jobs_list})


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
        companies = Company.objects.select_related('owner').all()
        users = Account.objects.all()

        # Get job seekers with more details
        job_seekers = users.filter(account_type="Employee").values(
            'id', 
            'first_name', 
            'last_name', 
            'email', 
            'date_of_birth',
            'contact_number',
            'address'
        )

        # Get companies with owner details
        companies_data = [{
            'id': company.id,
            'name': company.name,
            'owner_name': f"{company.owner.first_name} {company.owner.last_name}",
            'owner_email': company.owner.email,
            'address': company.address
        } for company in companies]

        # Get application statistics by date
        today = datetime.date.today()
        
        # Daily applications for the last 7 days
        daily_applications = []
        for i in range(7):
            date = today - datetime.timedelta(days=i)
            count = job_applications.filter(created_at__date=date).count()
            daily_applications.append({
                'date': date.strftime('%Y-%m-%d'),
                'count': count
            })

        # Monthly applications for the last 6 months
        monthly_applications = []
        for i in range(6):
            month_date = today - datetime.timedelta(days=30*i)
            count = job_applications.filter(
                created_at__year=month_date.year,
                created_at__month=month_date.month
            ).count()
            monthly_applications.append({
                'month': month_date.strftime('%B %Y'),
                'count': count
            })

        return JsonResponse({
            "statistics": {
                "total_jobs": jobs.count(),
                "total_applications": job_applications.count(),
                "total_companies": companies.count(),
                "total_users": users.count(),
            },
            "applications": {
                "daily": daily_applications,
                "monthly": monthly_applications
            },
            "jobSeekers": list(job_seekers),
            "companies": companies_data
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
        job.salary = data.get('salary', job.salary)
        job.salary_type = data.get('salary_type', job.salary_type)
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
            if (user.otp == otp):
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

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancel_application(request, id):
    if request.method == "POST":
        try:
            applications = JobApplication.objects.filter(job_id=id, applicant=request.user)
            if not applications.exists():
                return JsonResponse({"error": "No applications found for this job"}, status=404)
            
            for application in applications:
                if application.status == "Pending":
                    job = application.job
                    job.slots += 1
                    job.save()
                    application.delete()
                else:
                    return JsonResponse({"error": "Cannot cancel non-pending applications"}, status=400)
            
            return JsonResponse({"message": "Applications cancelled successfully"})
        except JobApplication.DoesNotExist:
            return JsonResponse({"error": "Application not found"}, status=404)
    return JsonResponse({"error": "Invalid request"}, status=400)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_job_status(request, id):
    try:
        job = Job.objects.get(id=id)
        is_applied = JobApplication.objects.filter(job=job, applicant=request.user).exists()
        is_saved = request.user.saved_jobs.filter(id=id).exists()
        
        if is_applied:
            application = JobApplication.objects.get(job=job, applicant=request.user)
            application_status = application.status
        else:
            application_status = None
            
        return JsonResponse({
            "is_applied": is_applied,
            "is_saved": is_saved,
            "application_status": application_status
        })
    except Job.DoesNotExist:
        return JsonResponse({"error": "Job not found"}, status=404)