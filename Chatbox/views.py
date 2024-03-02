from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import Room, Message
from django.http import HttpResponse, JsonResponse

from django.contrib.auth import authenticate
from django.contrib import messages,auth
from django.core.mail import send_mail
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from .models import CustomUser
from django.conf import settings


# Create your views here.



def register(request):
    if request.method == 'POST':
        email = request.POST['email']
        username = request.POST['username']
        phone = request.POST['phone']
        password = request.POST['password']
        if CustomUser.objects.filter(username=username).exists():
            messages.info(request, "Username is Taken")
            return redirect('register')
        elif len(phone) < 10 or len(phone) > 13:
            messages.error(request, "Phone number is not valid")
            return redirect('register')
        elif CustomUser.objects.filter(email=email).exists() or CustomUser.objects.filter(phone=phone).exists():
            messages.error(request, 'The user is already taken')
            return redirect('register')
        else:
            # Create a new user
            user = CustomUser.objects.create_user(email=email, username=username, phone=phone, password=password)
            user.is_active = False

            # Send verification email
            subject = 'Verify Your Email'
            message = 'Sending Email through Gmail'
            send_mail(subject, message, settings.EMAIL_HOST_USER, [email], fail_silently=True)
            messages.success(request, "Registration Successful. Please check your email for verification.")
            return redirect('home')  
    return render(request, 'register.html')



def user_login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid login credentials')
            return redirect('home')
    return render(request, 'login.html')


def home(request):
    return render(request, 'room.html')



@login_required
def checkview(request):
    """
    This view is responsible for handling the logic when a user checks or creates a chat room.
    
    Parameters:
    - request (HttpRequest): The HTTP request object.
    
    Returns:
    - HttpResponse: Redirects the user to the specified chat room.
    """
    room= request.POST.get('room_name')
    print("Checking room:", room)
    # Get the username of the logged-in user.
    username = request.user.username

    # Check if the room with the given name already exists.
    if Room.objects.filter(name=room).exists():
        print("Room exists.")
        return redirect('/'+room+'/?username='+username)
    else:
        # If the room does not exist, create a new room.
        new_room = Room.objects.create(name=room)
        new_room.save()
        return redirect('/'+room+'/?username='+username)


@login_required
def room(request, room):
    """
    This view renders the chat room page with relevant details.
    
    Parameters:
    - request (HttpRequest): The HTTP request object.
    - room (str): The name of the chat room.
    
    Returns:
    - HttpResponse: Renders the chatbox.html template with room details.
    """
    # Get the username of the logged-in user.
    username = request.user.username
    print("User is", username)
    # Retrieve details of the specified room from the database.
    room_details = Room.objects.get(name=room)
    # Render the chat room page with the necessary context.
    return render(request, 'chatbox.html', {
        'user_name': username,
        'room': room,
        'room_details': room_details
    })



def send(request):
    print("Sending message...")
    message = request.POST['message']
    username = request.POST['username']
    room_id = request.POST['room_id']
    print("message>>>>>>>", message, "username>>>>>>>>", username, "room_id>>>>", room_id)
    user_instance = CustomUser.objects.get(username=username)

    new_message = Message.objects.create(value=message, user=user_instance, room=room_id)
    new_message.save()

    return HttpResponse('Message sent successfully')


def getMessages(request, room):
    room_details = Room.objects.get(name=room)
    messages = Message.objects.filter(room=room_details).select_related('user')
    messages_data = []
    for message in messages:
        message_data = {
            'id': message.id,
            'value': message.value,
            'date': message.date,
            'user': message.user.username,
            'room': message.room,
        }
        messages_data.append(message_data)

    return JsonResponse({"messages": messages_data})

