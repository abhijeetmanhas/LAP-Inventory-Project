from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.forms import AuthenticationForm as LoginForm
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from .tokens import account_activation_token
from django.core.mail import EmailMessage

from .forms import SignUpForm, Comment, Return, RentForm, CommentForm, ReturnForm
from .models import Inventory, Rental, User
import email_to
server = email_to.EmailServer('smtp.gmail.com', 587, 'lteam0554@gmail.com', 'adhmt@lap16')


def sendConfMail(recp,item,qty,qtyUnit):
    server.quick_email(recp, 'Confirmation',
                    ["# Order Confirmed","Your order for {0} {1} {2} has been approved".format(str(qty),qtyUnit,item)],
                    style='h1 {color: blue}')

def checkAvailable(request):
    myobj = Inventory.objects.get(pk=request.POST['object'])
    if myobj.quantity >= (int)(request.POST['quantity']) and (int)(request.POST['quantity']) > 0:
            # myobj.quantity = myobj.quantity - (int)(request.POST['quantity'])
            # myobj.save()
        return True
    else:
        return False


def inventory(request):
    if request.user.is_authenticated:
        user = request.user
        print(user)
        invs = Inventory.objects.all()
        rents = Rental.objects.filter(user=user)
        name = request.user.get_short_name()
        newrent = RentForm(initial={'user': user.id})
        error = ""

        if request.method == 'POST':
            newrent = RentForm(request.POST, initial={'user': user.id})
            allcomments = []
            allreturns = []

            for rent in rents:
                aForm = [Comment(request.POST, initial={'pk': rent.pk})]
                bForm = [Return(request.POST, initial={'pk': rent.pk})]
                allreturns += bForm
                allcomments += aForm
            if len(allcomments) > 0:
                aForm = allcomments[0]
                bForm = allreturns[0]
                if aForm.is_valid() and 'comment' in request.POST:
                    txt = aForm['text'].value()
                    pk = aForm['pk'].value()
                    m = Rental.objects.get(pk=pk)
                    f = CommentForm({'id': pk, 'comments': txt}, instance=m)
                    if f.is_valid():
                        f.save()
                if bForm.is_valid() and 'return' in request.POST:
                    pk = bForm['pk'].value()
                    m = Rental.objects.get(pk=pk)
                    f = ReturnForm({'id': pk, 'approved': True,'requested':True}, instance=m)
                    if f.is_valid():
                        f.save()
            if 'new' in request.POST and newrent.is_valid():
                if not (checkAvailable(request)):
                    error += "Quantity not available."
        invs = Inventory.objects.all()
        rents = Rental.objects.filter(user=user)
        if request.method == "POST" and "new" in request.POST:
            mprice = float(request.POST['quantity'])*float(Inventory.objects.get(pk=request.POST['object']).price)
            newrent = RentForm(request.POST, initial={'user': user.id})
            if newrent.is_valid():
                inst = newrent.save(commit=False)
                inst.price = mprice
                inst.save()
        allcomments = []
        allreturns = []
        for rent in rents:
            aForm = [Comment(initial={'pk': rent.pk})]
            m = Rental.objects.get(pk=rent.pk)
            if rent.requested and rent.approved:
                myobj = rent.object
                if myobj.quantity >= (int)(rent.quantity) and (int)(rent.quantity) > 0:
                    print("loop")
                    myobj.quantity = myobj.quantity - (int)(rent.quantity)
                    myobj.save()
                    m.requested = False
                    m.save()

            bForm = [Return(initial={'pk': m.pk, 'ret': m.approved,'req':m.requested})]
            allreturns += bForm
            allcomments += aForm
        return render(request, 'index.html', {'name': name, 'invs': invs, 'rents': rents, 'newrent': newrent, 'error': error, 'allcomments': allcomments, 'allreturns': allreturns, })
    else:
        return HttpResponseRedirect('/new/')


def new(request):
    sendConfMail("144harshit@gmail.com","abcd",5,"gms")
    error = ""
    error1 = ""
    done = False
    if request.user.is_authenticated:
        return HttpResponseRedirect('/')
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        form1 = LoginForm(request.POST)
        if 'sign' in request.POST and not form.is_valid():
            error += "Invalid information/ Email already in use."
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            current_site = get_current_site(request)
            mail_subject = 'Activate your account.'
            message = render_to_string('acc_active_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': user.pk,
                'token': account_activation_token.make_token(user),
            })
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(mail_subject, message, to=[to_email])
            email.send()
            done = True
        elif 'log' in request.POST:
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('inventory')
            else:
                error1 += "Invalid email or password/ Account not verified. "
    else:
        form = SignUpForm()
        form1 = LoginForm()
    return render(request, 'new.html', {'form': form, 'form1': form1, 'error': error, 'error1': error1, 'done': done})


def activate(request, uidb64, token):
    try:
        user = User.objects.get(pk=uidb64)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    account_activation_token.check_token(user, token)
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return HttpResponse('Thank you for your email confirmation. Now you can login your account.')
    else:
        return HttpResponse('Activation link is invalid!')
