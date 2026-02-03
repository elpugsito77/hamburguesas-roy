import streamlit as st
import random
import urllib.parse

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
    .product-card {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #ddd;
        margin-bottom: 10px;
    }
    div[data-testid="stExpander"] div[role="button"] p {
        font-size: 1.1rem;
        font-weight: bold;
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
    st.session_state.vista = 'menu' # menu, producto, carrito
if 'producto_temp' not in st.session_state:
    st.session_state.producto_temp = None
if 'concepto_unico' not in st.session_state:
    st.session_state.concepto_unico = ""

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

def calcular_total():
    return sum(item['precio'] * item['cantidad'] for item in st.session_state.carrito)

def generar_link_whatsapp(nombre, direccion, metodo_pago, monto_pago, concepto):
    telefono = "5217298179223"
    mensaje = f"*PEDIDO NUEVO - HAMBURGUESAS ROY* 🍔\n"
    mensaje += f"--------------------------------\n"
    mensaje += f"👤 *Cliente:* {nombre}\n"
    if direccion:
        mensaje += f"📍 *Dirección:* {direccion}\n"
    mensaje += f"--------------------------------\n\n"
    mensaje += f"*ORDEN:*\n"
    
    for item in st.session_state.carrito:
        mensaje += f"▪️ {item['cantidad']}x {item['nombre']} (${item['precio'] * item['cantidad']})\n"
        if item['opciones']:
            mensaje += f"   - {', '.join(item['opciones'])}\n"
        if item['nota']:
            mensaje += f"   📝 Nota: {item['nota']}\n"
    
    total = calcular_total()
    mensaje += f"\n--------------------------------\n"
    mensaje += f"💰 *TOTAL A PAGAR: ${total}*\n"
    mensaje += f"--------------------------------\n"
    
    if metodo_pago == "Efectivo":
        cambio = float(monto_pago) - total if monto_pago else 0
        mensaje += f"💵 *PAGO EN EFECTIVO*\n"
        mensaje += f"   Paga con: ${monto_pago}\n"
        mensaje += f"   Cambio: ${cambio}\n"
    else:
        mensaje += f"🏦 *TRANSFERENCIA*\n"
        mensaje += f"   Concepto: *{concepto}*\n"
        
    return f"https://wa.me/{telefono}?text={urllib.parse.quote(mensaje)}"

# --- INTERFAZ PRINCIPAL ---

# 1. ENCABEZADO
st.title("🍔 Hamburguesas Roy")

# Botón flotante del carrito
if st.session_state.carrito:
    cols = st.columns([3, 2])
    with cols[0]:
        st.info(f"🛒 **Total: ${calcular_total()}** ({len(st.session_state.carrito)} items)")
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
        
        # Lógica para mostrar opciones (Checkbox o Radio)
        if prod.get("opciones"):
            st.write("---")
            if prod.get("tipo_opcion") == "check":
                st.subheader("Personaliza tus ingredientes")
                st.write("Marca los ingredientes que quieras **QUITAR**:")
                cols = st.columns(2)
                for i, op in enumerate(prod["opciones"]):
                    with cols[i % 2]: # Distribuir en 2 columnas
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
    
    if not st.session_state.carrito:
        st.warning("Tu carrito está vacío.")
        if st.button("Ir a pedir algo rico"):
            st.session_state.vista = 'menu'
            st.rerun()
    else:
        # Lista de items
        for item in st.session_state.carrito:
            with st.expander(f"{item['cantidad']}x {item['nombre']} - ${item['precio'] * item['cantidad']}", expanded=True):
                if item['opciones']:
                    st.write(f"**Detalles:** {', '.join(item['opciones'])}")
                if item['nota']:
                    st.write(f"**Nota:** {item['nota']}")
                if st.button("Eliminar", key=f"del_{item['id_unico']}"):
                    eliminar_del_carrito(item['id_unico'])
                    st.rerun()
        
        total = calcular_total()
        st.success(f"### Total a Pagar: ${total}")
        st.divider()
        
        # Formulario de Envío
        st.header("📍 Datos de Entrega")
        nombre = st.text_input("Tu Nombre")
        direccion = st.text_area("Dirección completa (Calle, Número, Colonia)", placeholder="O escribe 'Ubicación GPS' si la enviarás por chat.")
        
        st.header("💳 Método de Pago")
        metodo = st.radio("¿Cómo vas a pagar?", ["Efectivo", "Transferencia"], horizontal=True)
        
        monto_pago = 0
        concepto = ""
        
        if metodo == "Efectivo":
            monto_str = st.text_input("¿Con cuánto pagas? (Ej. 200, 500)", value="")
            try:
                if monto_str:
                    monto_pago = float(monto_str)
                    if monto_pago < total:
                        st.error(f"El monto debe ser mayor o igual a ${total}")
                    else:
                        st.success(f"Tu cambio será: ${monto_pago - total}")
            except:
                st.warning("Por favor ingresa solo números.")
        else:
            if not st.session_state.concepto_unico:
                st.session_state.concepto_unico = f"#ROY-{random.randint(1000,9999)}"
            concepto = st.session_state.concepto_unico
            st.info(f"⚠️ Usa este concepto en tu transferencia: **{concepto}**")
            
        st.write("---")
        
        # Botón Final
        if st.button("✅ Enviar Pedido por WhatsApp", type="primary", use_container_width=True):
            if not nombre:
                st.error("Falta tu nombre.")
            elif not direccion:
                st.error("Falta la dirección.")
            elif metodo == "Efectivo" and (monto_pago < total):
                st.error("Revisa el monto de pago en efectivo.")
            else:
                link = generar_link_whatsapp(nombre, direccion, metodo, monto_pago, concepto)
                st.markdown(f'<a href="{link}" target="_blank" style="display: inline-block; padding: 12px 20px; background-color: #25D366; color: white; text-align: center; text-decoration: none; font-size: 16px; border-radius: 5px; width: 100%;">👉 Toca aquí para abrir WhatsApp</a>', unsafe_allow_html=True)