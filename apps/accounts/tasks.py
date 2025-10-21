from django.template import Template, Context
from django.conf import settings
from django.core.mail import EmailMessage, send_mail

from MyStoreV2.celery import app
from .models import SubscribedUsers
from apps.shop.models import Product



@app.task
def send_subscribe_email(cd, *args, **kwargs):
    subject = "Оптово-розничный интернет-магазин."
    message = 'Вы успешно подписались на нашу рассылку!'

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[cd['email']],
        fail_silently=False
    )


REPORT_TEMPLATE = """   {% load static %}
                        <!DOCTYPE html>
                        <html lang="en">
                        <head>
                            <meta charset="UTF-8">
                            <title>Товары со скидкой!</title>
                        </head>
                        <body>
                            Вам предоставлена скидка на следующие товары:
                            <div>
                            {% for product in products %}
                                <p>Категория: {{ product.category }}</p>
                                <p>Название: {{ product.name }}</p>
                                <p>Цена: {{ product.price }}</p>
                                <p><img src="data:image/jpeg;base64,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"  height="100" width="100"></p>
                            {% endfor %}
                            </div>
                        </body> 
                        </html>"""

@app.task
def send_email_to_subscribers():
    products = Product.objects.order_by('-price')[:4]
    template = Template(REPORT_TEMPLATE)
    for email in SubscribedUsers.objects.all():
        mail = EmailMessage(
            subject='Товары со скидкой!',
            body=template.render(context=Context({'products': products})),
            from_email=settings.EMAIL_HOST_USER,
            to=[email],
        )
        mail.content_subtype = 'html'
        mail.send()
