from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import TrackingForm
from .utils import get_np_info, find_existing_page, append_text_block, create_notion_page

def index(request):
    if request.method == 'POST':
        form = TrackingForm(request.POST)
        if form.is_valid():
            try:
                app_number = form.cleaned_data['app_number']
                ttn = form.cleaned_data['ttn']
                social = form.cleaned_data['social'] or ''
                
                # Отримуємо інформацію з Нової Пошти
                price, paid = get_np_info(ttn)
                
                # Перевіряємо чи існує сторінка в Notion
                page_id = find_existing_page(ttn)
                status_text = "ОПЛАЧЕНО" if paid else "НЕ оплачено"
                short_ttn = ttn[-4:]
                
                log_text = (
                    f"Заявка №{app_number}-ТТН №{short_ttn}: "
                    f"{social} ${price} - {status_text}"
                )
                
                if page_id:
                    # ❗ ДУБЛІКАТ → ТІЛЬКИ КОМЕНТАР
                    append_text_block(page_id, log_text)
                    messages.success(request, "Додано коментар до існуючої заявки")
                else:
                    # ❗ НОВА → БЕЗ КОМЕНТАРЯ
                    create_notion_page(app_number, ttn, social, price, paid)
                    messages.success(request, "Створено нову заявку")
                
                context = {
                    'form': TrackingForm(),
                    'success': True,
                    'app_number': app_number,
                    'ttn': ttn,
                    'social': social,
                    'price': price,
                    'status': status_text,
                    'is_duplicate': bool(page_id)
                }
                
                return render(request, 'tracking/index.html', context)
                
            except Exception as e:
                messages.error(request, f"Помилка: {str(e)}")
                return render(request, 'tracking/index.html', {'form': form})
    else:
        form = TrackingForm()
    
    return render(request, 'tracking/index.html', {'form': form})