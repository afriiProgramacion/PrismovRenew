# Preguntas y Respuestas - Fase 2: Análisis de Utilidad y Aplicación (PRISMOV)

## Criterio 6a) Objetivos estratégicos
**¿Qué objetivos estratégicos específicos de la empresa aborda tu software?**
PRISMOV aborda el objetivo estratégico principal de maximizar la eficiencia operativa (OEE) y reducir los tiempos de inactividad no planificados (Downtime). Esto se logra mediante el monitoreo constante de los armónicos (THD) y parámetros críticos en el equipamiento industrial.
**¿Cómo se alinea el software con la estrategia general de digitalización?**
Se alinea digitalizando el ciclo de vida del dato (RA 5b) que antes se tomaba manualmente con multímetros, y enviando reportes automáticos mediante bots de mensajería (RA 5i, Telegram) de manera instantánea, democratizando la información de planta (OT) hacia los niveles de decisión de negocio (IT).

## Criterio 6b) Áreas de negocio y comunicaciones
**¿Qué áreas de la empresa (producción, negocio, comunicaciones) se ven más beneficiadas con tu software?**
1. *Producción*: Al recibir alertas preventivas y reportes automáticos, los técnicos de mantenimiento actúan antes de un fallo.
2. *Negocio/Gerencia*: Al disponer de informes ejecutivos (RA 2g) que traducen fallos THD en impacto financiero.
3. *Comunicaciones*: Integra a los operadores mediante bots conversacionales seguros, acelerando la toma de decisiones.
**¿Qué impacto operativo esperas en las operaciones diarias?**
Una reducción de los cuellos de botella mediante un tiempo medio de respuesta (MTTR) mucho menor y un ahorro de horas de análisis manual de logs en papel.

## Criterio 6c) Áreas susceptibles de digitalización
**¿Qué áreas de la empresa son más susceptibles de ser digitalizadas con tu software?**
El Área de Mantenimiento Preventivo/Predictivo y el Departamento de Control de Calidad Eléctrica. Estas áreas dependen de lecturas constantes que son fácilmente automatizables mediante el "Modo Automático" de PRISMOV.
**¿Cómo mejorará la digitalización las operaciones en esas áreas?**
Permitirá a los operarios programar análisis diarios y semanales ("Configurar programación"), pasando de un modelo "reactivo" (arreglar lo que se rompe) a uno completamente digitalizado y analítico ("preventivo").

## Criterio 6d) Encaje de áreas digitalizadas (AD)
**¿Cómo interactúan las áreas digitalizadas con las no digitalizadas?**
Las áreas digitalizadas (Mantenimiento con PRISMOV) generan un "Informe THD" que es exportado (por ejemplo, en PDF o papel si es necesario) a las áreas no digitalizadas (por ejemplo, operarios en línea o contabilidad pura sin ERP).
**¿Qué soluciones o mejoras propondrías para integrar estas áreas?**
Propondría una API REST documentada en PRISMOV para que otros sistemas (ERP/CRM) puedan consumir los datos THD generados internamente, forzando la digitalización horizontal de toda la cadena de valor.

## Criterio 6e) Necesidades presentes y futuras
**¿Qué necesidades actuales de la empresa resuelve tu software?**
Resuelve la falta de visibilidad en tiempo real del estado de la maquinaria (monitoreo THD continuo y reporte inmediato en Telegram) y elimina el error humano en la transcripción de datos (ciclo de vida del dato automatizado).
**Propuestas a futuro (Roadmap)**:
1. Migración a una App Web Multi-usuario.
2. Ingesta de datos de múltiples plantas industriales (IoT / Edge computing).
3. Capacidades de Inteligencia Artificial para el análisis predictivo.

## Criterio 6f) Relación con tecnologías
**¿Qué tecnologías habilitadoras has empleado y cómo impactan en las áreas de la empresa?**
- **Computación en la Nube / APIs y Bots (Nivel Aplicación)**: Uso de Telegram y cron-jobs en la nube o servidores on-premise (RA 5f). Impacta agilizando las comunicaciones e informes.
- **Interfaces Gráficas e Informes Dinámicos**: Interfaces PyQt5 con modo oscuro para la visualización humana ergonómica en las plantas.
**¿Qué beneficios específicos aporta la implantación de estas tecnologías?**
Interactividad, reducción de fricciones en la adopción del software gracias a una GUI moderna y profesional y disponibilidad de la información asíncrona mediante Telegram.

## Criterio 6g) Brechas de seguridad
**¿Qué posibles brechas de seguridad podrían surgir al implementar tu software?**
1. Exposición de tokens de API y URLs de base de datos en código fuente visible.
2. Interceptación de datos en tránsito si los reportes no van cifrados.
3. Acceso no autorizado de operarios locales a configuraciones del programa.
**¿Qué medidas concretas propondrías para mitigarlas?**
Ya implementadas: Desvinculación de Supabase explícita y gestión de códigos únicos de vinculación de un solo uso (Tokenization) para Telegram (RA 5i).
A implementar: Encriptación en reposo (AES) del archivo `historial.json` y uso de variables de entorno `.env` en lugar de guardar credenciales en el código base.

## Criterio 6h) Tratamiento de datos y análisis
**¿Cómo se gestionan los datos en tu software y qué metodologías utilizas?**
Los datos brutos (sensórica) se recogen, formatean, agrupan y se almacenan temporalmente gestionando su ciclo de vida íntegro (RA 5b). Después, algoritmos internos (en `prismov.py`) extraen índices y comparativas de negocio.
**¿Qué haces para garantizar la calidad y consistencia de los datos?**
Al usar formatos estandarizados (`.json`) y validaciones previo a la ejecución del análisis o programación de horas (como `QTimeEdit` o `QSpinBox` que fuerzan el intervalo de minutos), se evita la inyección de datos impuros por parte del usuario final.
