import streamlit as st


def calculate_retail_book_price(
    quantity,        # print run (units
    format_code,     # "A4", "A5", "A6"
    vat_percent,     # VAT (%)
    discount_percent,
    format_code1
):

    # ===== BASE REFERENCE MODEL =====
    # A5, 200 pages, 3000 copies

    base_pages = 200
    base_quantity = 100

    format_coefficients = {
        "Default": 1.0,
        "Pro": 1.2,
        "Max": 1.5
    }

    if format_code not in format_coefficients:
        raise ValueError("format_code must be 'Default', 'Pro' or 'Max'")

    format_coefficients1 = {
        "128 Gb": 1.0,
        "256 Gb": 1.2,
        "512 Gb": 1.4,
        "1 Tb": 1.5
    }

    if format_code1 not in format_coefficients1:
        raise ValueError("format_code must be '128 Gb', '256 Gb' or '512 Gb', '1 Tb")

    format_factor = format_coefficients[format_code]
    pages_factor = format_coefficients1[format_code1] * base_pages
    quantity_factor = quantity / base_quantity

    # ===== FIXED RUSSIAN MARKET COSTS (BASE MODEL) =====

    materials_cost_base = 85000
    labor_cost_base = 30000
    amortization_cost_base = 12500

    overhead_prod_percent = 20
    overhead_admin_percent = 15

    design_cost = 25000
    editing_cost = 20000
    isbn_cost = 3000
    marketing_cost = 50000
    logistics_cost = 20000

    publisher_margin_percent = 30
    retailer_markup_percent = 70

    # ===== SCALE COSTS =====

    materials_cost = (
        materials_cost_base *
        quantity_factor *
        format_factor +
        pages_factor
    )

    labor_cost = labor_cost_base * quantity_factor
    amortization_cost = amortization_cost_base * quantity_factor

    # ===== BASE COSTS =====

    base_cost_total = (
        materials_cost +
        labor_cost +
        amortization_cost
    )

    # ===== OVERHEAD COSTS =====

    overhead_production = base_cost_total * overhead_prod_percent / 100
    overhead_admin = base_cost_total * overhead_admin_percent / 100

    commercial_costs = (
        design_cost +
        editing_cost +
        isbn_cost +
        marketing_cost +
        logistics_cost
    )

    overhead_total = (
        overhead_production +
        overhead_admin +
        commercial_costs
    )

    # ===== FULL COST =====

    full_cost_total = base_cost_total + overhead_total
    full_cost_per_unit = full_cost_total / quantity

    # ===== WHOLESALE & RETAIL =====

    publisher_profit = full_cost_per_unit * publisher_margin_percent / 100
    wholesale_price_no_vat = full_cost_per_unit + publisher_profit
    wholesale_price_with_vat = wholesale_price_no_vat * (1 + vat_percent / 100)

    retailer_markup = wholesale_price_with_vat * retailer_markup_percent / 100
    retail_price = wholesale_price_with_vat + retailer_markup

    final_price = retail_price * (1 - discount_percent / 100)

    return round(final_price, 2)


# ===== STREAMLIT APP =====

st.set_page_config(page_title="Калькулятор цены смартфона", layout="centered")

st.title(" Калькулятор розничной цены смартфона")
st.markdown("---")

# Создаем контейнер для формы
with st.form("price_calculator_form"):
    col1, col2 = st.columns(2)

    with col1:
        quantity = st.text_input(
            "Количество смартфонов",
            value="100",
            help="Введите количество смартфонов"
        )

    with col2:
        format_code1 = st.selectbox(
            "Память",
            options=["128 Gb", "256 Gb", "512 Gb", "1 Tb"],
            help="Выберите размер памяти: 128 Gb, 256 Gb, 512 Gb, 1 Tb."
        )

    col3, col4 = st.columns(2)

    with col3:
        format_code = st.selectbox(
            "Модель",
            options=["Default", "Pro", "Max"],
            help="Выберите модель: Default (обычная), Pro (улучшенная), Max (максимальная)"
        )

    with col4:
        vat_percent = st.text_input(
            "НДС (%)",
            value="20",
            help="Введите процент НДС"
        )

    discount_percent = st.text_input(
        "Скидка (%)",
        value="0",
        help="Введите процент скидки"
    )

    submit_button = st.form_submit_button("Рассчитать цену", use_container_width=True)

st.markdown("---")

# Обработка форм и расчет
if submit_button:
    try:
        # Преобразуем текстовые поля в числа
        quantity_val = int(quantity)
        vat_val = float(vat_percent)
        discount_val = float(discount_percent)

        # Валидация
        if quantity_val <= 0:
            st.error("❌ Количество копий должно быть больше 0")
        elif vat_val < 0:
            st.error("❌ НДС не может быть отрицательным")
        elif discount_val < 0 or discount_val > 100:
            st.error("❌ Скидка должна быть от 0 до 100%")
        else:
            # Расчет цены
            final_price = calculate_retail_book_price(
                quantity=quantity_val,
                format_code1=format_code1,
                format_code=format_code,
                vat_percent=vat_val,
                discount_percent=discount_val
            )

            # Вывод результата
            st.success(" Расчет выполнен успешно!")

            col1, col2, col3 = st.columns(3)
            with col2:
                st.metric(
                    label="Розничная цена",
                    value=f"₽ {final_price:.2f}",
                    label_visibility="visible"
                )

            # Дополнительная информация
            st.markdown("###  Параметры расчета:")
            info_col1, info_col2 = st.columns(2)
            with info_col1:
                st.write(f"**Количество:** {quantity_val} копий")
                st.write(f"**Размер памяти:** {format_code1}")
                st.write(f"**Модель:** {format_code}")
            with info_col2:
                st.write(f"**НДС:** {vat_val}%")
                st.write(f"**Скидка:** {discount_val}%")

    except ValueError:
        st.error("❌ Пожалуйста, введите корректные числовые значения")
    except Exception as e:
        st.error(f"❌ Ошибка при расчете: {str(e)}")