import streamlit as st
import random
import urllib.parse
from datetime import datetime

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Hamburguesas Roy",
    page_icon="🍔",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- ESTILOS PERSONALIZADOS (CSS) ---
st.markdown("""
<style>
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        font-weight: bold;
    }
    .price-tag {
        color: #e65100;
        font-weight: bold;
        font-size: 1.2rem;
    }
    .folio-tag {
        background-color: #ffe0b2;
        padding: 5px 10px;
        border-radius: 5px;
        color: #e65100;
        font-weight: bold;
        border: 1px solid #e65100;
        display: inline-block;
        margin-bottom: 10px;
    }
    .total-box {
        background-color: #e8f5e9;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #4caf50;
        margin-top: 10px;
    }
</style>
""", unsafe_allow_html=True)

# --- DATOS DEL MENÚ ---
ING_BASE_HAMBURGUESA = ["Sin Cebolla", "Sin Jitomate", "Sin Lechuga", "Sin Chile", "Sin Queso Amarillo", "Sin Aderezos"]
ING_EXTRA_HAWAIANA = ["Sin Piña", "Sin Tocino", "Sin Salchicha", "Sin Queso Oaxaca"]

# Hot Dogs: Todos llevan tocino base
ING_BASE_HOTDOG = ["Sin Jitomate", "Sin Cebolla", "Sin Chile", "Sin Aderezos", "Sin Tocino"]
ING_EXTRA_QUESO = ["Sin Queso Oaxaca"]
ING_EXTRA_ESPECIAL = ["Sin Queso Amarillo", "Sin Queso Oaxaca", "Sin Jamón", "Sin Piña"]

PRODUCTOS = [
    # Hamburguesas
    {"id": 1, "nombre": "Hamburguesa Sencilla", "descripcion": "Res, queso amarillo, vegetales.", "precio": 60, "categoria": "Hamburguesas", "tipo_opcion": "check", "opciones": ING_BASE_HAMBURGUESA},
    {"id": 2, "nombre": "Hamburguesa Hawaiana", "descripcion": "Piña, tocino, salchicha, queso Oaxaca.", "precio": 70, "categoria": "Hamburguesas", "tipo_opcion": "check", "opciones": ING_BASE_HAMBURGUESA + ING_EXTRA_HAWAIANA},
    {"id": 3, "nombre": "Hamburguesa Especial", "descripcion": "Piña, tocino, salchicha, Oaxaca, doble sabor.", "precio": 90, "categoria": "Hamburguesas", "tipo_opcion": "check", "opciones": ING_BASE_HAMBURGUESA + ING_EXTRA_HAWAIANA},
    
    # Hot Dogs
    {"id": 4, "nombre": "Hot Dog Sencillo", "descripcion": "Salchicha, tocino, vegetales.", "precio": 25, "categoria": "Hot Dogs", "tipo_opcion": "check", "opciones": ING_BASE_HOTDOG},
    {"id": 5, "nombre": "Hot Dog con Queso", "descripcion": "Salchicha, tocino y Queso Oaxaca.", "precio": 35, "categoria": "Hot Dogs", "tipo_opcion": "check", "opciones": ING_BASE_HOTDOG + ING_EXTRA_QUESO},
    {"id": 6, "nombre": "Hot Dog Especial", "descripcion": "Jamón, Q. Amarillo, Q. Oaxaca, Piña.", "precio": 40, "categoria": "Hot Dogs", "tipo_opcion": "check", "opciones": ING_BASE_HOTDOG + ING_EXTRA_ESPECIAL},
    
    # Bebidas
    {"id": 7, "nombre": "Coca Cola", "descripcion": "Botella 600ml.", "precio": 25, "categoria": "Bebidas", "tipo_opcion": "radio", "titulo_opcion": "Presentación", "opciones": ["Botella 600ml"]},
    {"id": 8, "nombre": "Jarritos", "descripcion": "Refresco sabor frutal (600ml).", "precio": 25, "categoria": "Bebidas", "tipo_opcion": "radio", "titulo_opcion": "Sabor", "opciones": ["Mandarina", "Tamarindo", "Piña", "Tutifruti", "Limón"]}
]

# --- GESTIÓN DEL ESTADO (CARRITO) ---
if 'carrito' not in st.session_state:
    st.session_state.carrito = []
if 'vista' not in st.session_state:
    st.session_state.vista = 'menu'
if 'producto_temp' not in st.session_state:
    st.session_state.producto_temp = None
# Generamos el folio UNA VEZ por sesión basado en el momento de inicio
if 'folio_actual' not in st.session_state:
    now = datetime.now()
    st.session_state.folio_actual = f"ROY-{now.strftime('%d%H%M')}"

# --- FUNCIONES ---
def agregar_al_carrito(producto, cantidad, opciones_seleccionadas, nota):
    item = {
        "id_unico": random.randint(1000, 99999),
        "nombre": producto["nombre"],
        "precio": producto["precio"],
        "cantidad": cantidad,
        "opciones": opciones_seleccionadas,
        "nota": nota
    }
    st.session_state.carrito.append(item)
    st.session_state.vista = 'menu'
    st.session_state.producto_temp = None

def eliminar_del_carrito(id_unico):
    st.session_state.carrito = [p for p in st.session_state.carrito if p['id_unico'] != id_unico]

def calcular_subtotal():
    return sum(item['precio'] * item['cantidad'] for item in st.session_state.carrito)

def calcular_costo_envio(subtotal, zona):
    costo = 0
    if zona == "Hacienda de las Fuentes":
        # Cobra 10 si es menos de 100
        if subtotal < 100:
            costo = 10
    elif zona == "Lomas Virreyes":
        # Cobra 20 si es menos de 200
        if subtotal < 200:
            costo = 20
    elif zona == "Villas del Campo":
        # Siempre cobra 30
        costo = 30
    # "Otro lado" asumimos 0 o a convenir, aquí lo dejamos en 0 para sumar
    return costo

def generar_link_whatsapp(nombre, direccion, zona, metodo_pago, monto_pago, folio, subtotal, costo_envio, total_final):
    # Número actualizado
    telefono = "5215669328454"
    
    # Construcción del mensaje
    mensaje = f"📄 *FOLIO: {folio}*\n"
    mensaje += f"*PEDIDO - HAMBURGUESAS ROY* 🍔\n"
    mensaje += f"--------------------------------\n"
    mensaje += f"👤 *Cliente:* {nombre}\n"
    mensaje += f"🏘️ *Zona:* {zona}\n"
    mensaje += f"📍 *Dirección:* {direccion}\n"
    mensaje += f"--------------------------------\n\n"
    mensaje += f"*ORDEN:*\n"
    
    for item in st.session_state.carrito:
        mensaje += f"▪️ {item['cantidad']}x {item['nombre']} (${item['precio'] * item['cantidad']})\n"
        if item['opciones']:
            mensaje += f"   - {', '.join(item['opciones'])}\n"
        if item['nota']:
            mensaje += f"   📝 Nota: {item['nota']}\n"
    
    mensaje += f"\n--------------------------------\n"
    mensaje += f"Subtotal: ${subtotal}\n"
    if costo_envio > 0:
        mensaje += f"Envío ({zona}): +${costo_envio}\n"
    else:
        mensaje += f"Envío: GRATIS\n"
    mensaje += f"💰 *TOTAL A PAGAR: ${total_final}*\n"
    mensaje += f"--------------------------------\n"
    
    if metodo_pago == "Efectivo":
        cambio = float(monto_pago) - total_final if monto_pago else 0
        mensaje += f"💵 *PAGO EN EFECTIVO*\n"
        mensaje += f"   Paga con: ${monto_pago}\n"
        mensaje += f"   Cambio: ${cambio}\n"
    else:
        mensaje += f"🏦 *TRANSFERENCIA*\n"
        mensaje += f"   Concepto/Ref: *{folio}*\n"
        
    return f"https://wa.me/{telefono}?text={urllib.parse.quote(mensaje)}"

# --- INTERFAZ PRINCIPAL ---

# 1. ENCABEZADO SIMPLE
st.title("🍔 Hamburguesas Roy")

# Botón flotante del carrito
if st.session_state.carrito:
    subtotal_actual = calcular_subtotal()
    cols = st.columns([3, 2])
    with cols[0]:
        st.info(f"🛒 **Subtotal: ${subtotal_actual}**")
    with cols[1]:
        if st.button("Ver Pedido →", type="primary", use_container_width=True):
            st.session_state.vista = 'carrito'
            st.rerun()

st.divider()

# 2. LÓGICA DE VISTAS
if st.session_state.vista == 'menu':
    # --- MENÚ POR TABS ---
    tab1, tab2, tab3 = st.tabs(["🍔 Hamburguesas", "🌭 Hot Dogs", "🥤 Bebidas"])
    
    def mostrar_productos(categoria):
        productos_filtrados = [p for p in PRODUCTOS if p['categoria'] == categoria]
        for prod in productos_filtrados:
            with st.container():
                c1, c2 = st.columns([3, 1])
                with c1:
                    st.subheader(prod['nombre'])
                    st.caption(prod['descripcion'])
                    st.markdown(f"<span class='price-tag'>${prod['precio']}</span>", unsafe_allow_html=True)
                with c2:
                    st.write("") # Espaciador
                    if st.button("➕", key=f"add_{prod['id']}"):
                        st.session_state.producto_temp = prod
                        st.session_state.vista = 'producto'
                        st.rerun()
                st.divider()

    with tab1:
        mostrar_productos("Hamburguesas")
    with tab2:
        mostrar_productos("Hot Dogs")
    with tab3:
        mostrar_productos("Bebidas")

elif st.session_state.vista == 'producto':
    # --- DETALLE PRODUCTO ---
    prod = st.session_state.producto_temp
    
    if st.button("← Regresar al Menú"):
        st.session_state.vista = 'menu'
        st.rerun()
        
    st.header(f"{prod['nombre']}")
    st.write(prod['descripcion'])
    st.markdown(f"### Precio: ${prod['precio']}")
    
    with st.form("form_producto"):
        cantidad = st.number_input("Cantidad", min_value=1, value=1, step=1)
        
        opciones_elegidas = []
        
        if prod.get("opciones"):
            st.write("---")
            if prod.get("tipo_opcion") == "check":
                st.subheader("Personaliza tus ingredientes")
                st.write("Marca los ingredientes que quieras **QUITAR**:")
                cols = st.columns(2)
                for i, op in enumerate(prod["opciones"]):
                    with cols[i % 2]: 
                        if st.checkbox(op):
                            opciones_elegidas.append(op)
            
            elif prod.get("tipo_opcion") == "radio":
                titulo = prod.get("titulo_opcion", "Selecciona una opción")
                st.subheader(titulo)
                seleccion = st.radio(f"Elige {titulo.lower()}:", prod["opciones"])
                opciones_elegidas.append(f"{titulo}: {seleccion}")
        
        st.write("---")
        nota_extra = st.text_area("¿Alguna instrucción especial?", placeholder="Ej. Carne bien cocida, partir a la mitad...")
        
        submitted = st.form_submit_button(f"Agregar al Pedido", type="primary")
        if submitted:
            agregar_al_carrito(prod, cantidad, opciones_elegidas, nota_extra)
            st.success("¡Producto agregado!")
            st.rerun()

elif st.session_state.vista == 'carrito':
    # --- CARRITO Y PAGO ---
    if st.button("← Volver al Menú"):
        st.session_state.vista = 'menu'
        st.rerun()
        
    st.header("🛒 Tu Carrito")
    
    now = datetime.now()
    folio_actual = f"ROY-{now.strftime('%d%H%M%S')}" 
    
    st.markdown(f"<div class='folio-tag'>📄 Folio: {folio_actual}</div>", unsafe_allow_html=True)

    if not st.session_state.carrito:
        st.warning("Tu carrito está vacío.")
        if st.button("Ir a pedir algo rico"):
            st.session_state.vista = 'menu'
            st.rerun()
    else:
        # Listado de productos
        for item in st.session_state.carrito:
            with st.expander(f"{item['cantidad']}x {item['nombre']} - ${item['precio'] * item['cantidad']}", expanded=True):
                if item['opciones']:
                    st.write(f"**Detalles:** {', '.join(item['opciones'])}")
                if item['nota']:
                    st.write(f"**Nota:** {item['nota']}")
                if st.button("Eliminar", key=f"del_{item['id_unico']}"):
                    eliminar_del_carrito(item['id_unico'])
                    st.rerun()
        
        # --- CÁLCULO DE TOTALES ---
        st.divider()
        st.header("📍 Datos de Entrega")
        
        # Selector de Zona
        zonas = ["Hacienda de las Fuentes", "Lomas Virreyes", "Villas del Campo", "Otro lado"]
        zona_seleccionada = st.selectbox("Selecciona tu zona:", zonas)
        
        nombre = st.text_input("Tu Nombre")
        direccion_escrita = st.text_area("Dirección exacta (Calle y Número)", placeholder="Ej. Calle Principal #123")
        
        # Cálculos de precio
        subtotal = calcular_subtotal()
        costo_envio = calcular_costo_envio(subtotal, zona_seleccionada)
        total_final = subtotal + costo_envio
        
        # Mostrar desglose bonito
        st.markdown(f"""
        <div class="total-box">
            <p style="margin:0;">Subtotal: <b>${subtotal}</b></p>
            <p style="margin:0;">Costo de envío: <b>${costo_envio}</b> <small>({zona_seleccionada})</small></p>
            <hr style="margin:10px 0;">
            <h3 style="margin:0; color: #2e7d32;">Total a Pagar: ${total_final}</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Avisos de envío según zona
        if zona_seleccionada == "Hacienda de las Fuentes" and subtotal < 100:
            st.caption("ℹ️ Envío $10 porque la compra es menor a $100.")
        elif zona_seleccionada == "Lomas Virreyes" and subtotal < 200:
            st.caption("ℹ️ Envío $20 porque la compra es menor a $200.")
        elif zona_seleccionada == "Villas del Campo":
            st.caption("ℹ️ Envío fijo de $30 a Villas.")
        elif zona_seleccionada == "Hacienda de las Fuentes" and subtotal >= 100:
             st.caption("✅ ¡Envío GRATIS por compra mayor a $100!")
        elif zona_seleccionada == "Lomas Virreyes" and subtotal >= 200:
             st.caption("✅ ¡Envío GRATIS por compra mayor a $200!")

        st.header("💳 Método de Pago")
        metodo = st.radio("¿Cómo vas a pagar?", ["Efectivo", "Transferencia"], horizontal=True)
        
        monto_pago = 0
        
        if metodo == "Efectivo":
            monto_str = st.text_input("¿Con cuánto pagas?", value="")
            try:
                if monto_str:
                    monto_pago = float(monto_str)
                    if monto_pago < total_final:
                        st.error(f"El monto debe ser mayor o igual a ${total_final}")
                    else:
                        st.success(f"Tu cambio será: ${monto_pago - total_final}")
            except:
                st.warning("Ingresa solo números.")
        else:
            st.info(f"⚠️ Usa este folio en el concepto de tu transferencia: **{folio_actual}**")
            
        st.write("---")
        
        if st.button("✅ Enviar Pedido por WhatsApp", type="primary", use_container_width=True):
            if not nombre:
                st.error("Falta tu nombre.")
            elif not direccion_escrita:
                st.error("Falta escribir la dirección.")
            elif metodo == "Efectivo" and (monto_pago < total_final):
                st.error("Revisa el monto de pago.")
            else:
                link = generar_link_whatsapp(nombre, direccion_escrita, zona_seleccionada, metodo, monto_pago, folio_actual, subtotal, costo_envio, total_final)
                st.markdown(f'<a href="{link}" target="_blank" style="display: inline-block; padding: 12px 20px; background-color: #25D366; color: white; text-align: center; text-decoration: none; font-size: 16px; border-radius: 5px; width: 100%;">👉 Toca aquí para abrir WhatsApp</a>', unsafe_allow_html=True)
