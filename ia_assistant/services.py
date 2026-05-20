import re


class QhaliAIService:
    def __init__(self):
        self.knowledge_base = {
            "planes": (
                "Qhalisys+ tiene planes Gratis, Básico S/50, Intermedio S/90, "
                "Avanzado S/150 y Custom a medida."
            ),
            "pos": (
                "El módulo POS permite vender rápido, gestionar ticket actual, cliente, "
                "comprobante, caja activa y cobro optimizado."
            ),
            "inventario": (
                "El inventario maestro permite controlar productos, laboratorios, categorías, "
                "stock, recetas, vencimientos y alertas críticas."
            ),
            "compras": (
                "El módulo de compras permite registrar proveedor, sucursal destino, productos recibidos, "
                "lote, vencimiento, costo y subtotal."
            ),
            "traslados": (
                "El módulo de traslados permite mover mercadería entre sedes con trazabilidad y control."
            ),
            "facturacion": (
                "Qhalisys+ incluye facturación electrónica para ticket, boleta, factura, series, "
                "correlativos y configuración de comprobantes."
            ),
            "cotizaciones": (
                "El sistema puede generar cotizaciones para clientes y convertirlas en parte del flujo comercial."
            ),
            "ia": (
                "Qhalisys+ incorpora búsqueda inteligente para encontrar productos, clientes, módulos, "
                "comprobantes y acciones frecuentes."
            ),
            "whatsapp": (
                "Puedes contactar a soporte al +51 916 393 838 o a ventas al +51 944 351 698."
            ),
        }

    def clean_text(self, text):
        text = text.lower().strip()
        text = re.sub(r"[^\w\sáéíóúñ]", "", text)
        return text

    def detect_intent(self, message):
        text = self.clean_text(message)

        intents = {
            "planes": ["plan", "planes", "precio", "costo", "cuanto", "mensual", "gratis", "basico", "intermedio", "avanzado"],
            "pos": ["pos", "venta", "vender", "ticket", "caja", "cliente"],
            "inventario": ["inventario", "stock", "producto", "productos", "laboratorio", "vencimiento", "receta"],
            "compras": ["compra", "compras", "proveedor", "lote", "entrada", "recepcion"],
            "traslados": ["traslado", "traslados", "sede", "sucursal", "mercaderia"],
            "facturacion": ["factura", "boleta", "sunat", "facturacion", "comprobante", "serie", "correlativo"],
            "cotizaciones": ["cotizacion", "cotizaciones", "presupuesto"],
            "ia": ["ia", "inteligencia", "buscar", "busqueda", "asistente", "agente"],
            "whatsapp": ["whatsapp", "contacto", "soporte", "ventas", "numero", "llamar"],
        }

        for intent, keywords in intents.items():
            if any(keyword in text for keyword in keywords):
                return intent

        return "general"

    def get_response(self, message):
        intent = self.detect_intent(message)

        if intent in self.knowledge_base:
            return {
                "intent": intent,
                "answer": self.knowledge_base[intent],
                "suggestions": self.get_suggestions(intent),
            }

        return {
            "intent": "general",
            "answer": (
                "Soy Qhali AI, el asistente inteligente de Qhalisys+. "
                "Puedo ayudarte con POS, inventario, compras, traslados, facturación electrónica, "
                "planes, soporte y ventas."
            ),
            "suggestions": [
                "¿Qué incluye el plan básico?",
                "¿Cómo funciona el POS?",
                "¿Qhalisys tiene facturación electrónica?",
                "Quiero hablar con ventas",
            ],
        }

    def get_suggestions(self, intent):
        suggestions = {
            "planes": ["Ver plan básico", "Ver plan avanzado", "Hablar con ventas"],
            "pos": ["Explicar caja activa", "Ver ventas POS", "Consultar facturación"],
            "inventario": ["Consultar stock", "Ver productos críticos", "Explicar vencimientos"],
            "compras": ["Registrar compra", "Consultar proveedores", "Explicar lotes"],
            "traslados": ["Mover entre sedes", "Control por sucursal", "Consultar inventario"],
            "facturacion": ["Emitir boleta", "Emitir factura", "Configurar series"],
            "ia": ["Buscar producto", "Buscar módulo", "Consultar acciones rápidas"],
            "whatsapp": ["Contactar soporte", "Contactar ventas", "Solicitar demo"],
        }

        return suggestions.get(intent, [])