"""
Preguntas frecuentes de cada ley (3 por ley) para el bloque visible de la página de test general.
Cada respuesta está comprobada contra el texto consolidado del BOE de NegocioOposiciones/fuentes/
(22/10/2026) y cita su artículo. Si una ley se reforma, revisar aquí también.
"""
import re

FAQ = {
    "ley-55-2003": [
        ("¿Qué tipo de relación tiene el personal estatutario?",
         "Una relación funcionarial especial con los servicios de salud del Sistema Nacional de Salud, regulada por el Estatuto Marco (art. 1)."),
        ("¿Cuántos días de vacaciones tiene el personal estatutario?",
         "Como mínimo 30 días naturales al año, o la parte proporcional al tiempo de servicios. Solo se pueden cambiar por dinero al terminar la relación de servicios (art. 53)."),
        ("¿Cuál es la jornada máxima sumando guardias?",
         "La jornada ordinaria y la complementaria juntas no pueden pasar de 48 horas semanales de trabajo efectivo de promedio en cómputo semestral, salvo otro cómputo pactado (art. 48.2)."),
    ],
    "ley-41-2002": [
        ("¿El consentimiento informado tiene que ser por escrito?",
         "Por regla general es verbal. Es por escrito en intervenciones quirúrgicas, procedimientos diagnósticos y terapéuticos invasores y, en general, en los que suponen riesgos de notoria y previsible repercusión negativa (art. 8.2)."),
        ("¿Puede un menor de 16 años o más decidir sobre su tratamiento?",
         "Sí: con los menores emancipados o mayores de 16 años no cabe el consentimiento por representación, salvo que se trate de una actuación de grave riesgo para su vida o salud según el facultativo (art. 9.4)."),
        ("¿Cuánto tiempo se conserva la historia clínica?",
         "El tiempo adecuado a cada caso y, como mínimo, cinco años desde la fecha del alta de cada proceso asistencial (art. 17.1)."),
    ],
    "ley-14-1986": [
        ("¿Qué son las Áreas de Salud?",
         "Las estructuras fundamentales del sistema sanitario: gestionan de forma unitaria los centros del Servicio de Salud de la comunidad autónoma en su territorio (art. 56.2)."),
        ("¿Cuánta población cubre un Área de Salud?",
         "Como regla general, entre 200.000 y 250.000 habitantes, con excepciones para Baleares, Canarias, Ceuta y Melilla. Cada provincia tiene al menos un Área (art. 56.5)."),
        ("¿Qué es la zona básica de salud?",
         "El marco territorial de la atención primaria, donde desarrollan su actividad los Centros de Salud (art. 63)."),
    ],
    "ley-44-2003": [
        ("¿Qué profesiones sanitarias son de nivel Diplomado?",
         "Enfermería, Fisioterapia, Terapia Ocupacional, Podología, Óptica y Optometría, Logopedia y Nutrición Humana y Dietética, además de sus especialistas (art. 2.2.b)."),
        ("¿Los TCAE son profesionales sanitarios según esta ley?",
         "Sí, como profesionales del área sanitaria de formación profesional de grado medio, junto con los Técnicos en Farmacia (art. 3.2.b)."),
        ("¿Cuántos grados tiene el desarrollo profesional?",
         "Cuatro grados (las Administraciones pueden añadir uno inicial). Para el primero hacen falta cinco años de ejercicio profesional (art. 38.1)."),
    ],
    "ley-16-2003": [
        ("¿Quién tiene derecho a la atención sanitaria?",
         "Todas las personas con nacionalidad española y las extranjeras que tengan establecida su residencia en España (art. 3.1)."),
        ("¿En qué modalidades se divide la cartera común de servicios?",
         "En tres: cartera común básica de servicios asistenciales, cartera común suplementaria y cartera común de servicios accesorios (art. 8.2)."),
        ("¿Qué es el Consejo Interterritorial del SNS?",
         "El órgano permanente de coordinación, cooperación, comunicación e información de los servicios de salud entre ellos y con la Administración del Estado. Cada año eleva una memoria al Senado (art. 69)."),
    ],
    "ley-31-1995": [
        ("¿Puede un trabajador dejar su puesto ante un riesgo grave?",
         "Sí: tiene derecho a interrumpir su actividad y abandonar el lugar de trabajo, si es necesario, cuando considere que entraña un riesgo grave e inminente para su vida o su salud (art. 21.2)."),
        ("¿Cuántos Delegados de Prevención corresponden a una empresa?",
         "Hasta 30 trabajadores, el Delegado de Personal; de 31 a 49, uno; de 50 a 100, dos; de 101 a 500, tres; y así hasta 8 a partir de 4.001 (art. 35.2)."),
        ("¿Cuándo hay que crear un Comité de Seguridad y Salud?",
         "En las empresas o centros de trabajo con 50 o más trabajadores. Es paritario y se reúne cada trimestre (art. 38)."),
    ],
    "lo-3-2007": [
        ("¿Qué es la composición equilibrada?",
         "Que en el conjunto de que se trate ninguno de los dos sexos supere el 60 % ni baje del 40 % (disposición adicional primera)."),
        ("¿Qué empresas tienen que tener plan de igualdad?",
         "Las de cincuenta o más trabajadores, además de las que lo exija su convenio colectivo o la autoridad laboral (art. 45)."),
        ("¿Qué diferencia hay entre acoso sexual y acoso por razón de sexo?",
         "El acoso sexual es un comportamiento de naturaleza sexual; el acoso por razón de sexo se hace en función del sexo de la persona. Ambos atentan contra su dignidad y se consideran discriminatorios (art. 7)."),
    ],
    "lo-3-2018": [
        ("¿Desde qué edad puede un menor consentir el uso de sus datos?",
         "Desde los catorce años. Por debajo de esa edad hace falta el consentimiento de quien tenga la patria potestad o tutela (art. 7)."),
        ("¿Cuánto tiempo se guardan las imágenes de videovigilancia?",
         "Como máximo un mes desde que se graban, salvo que deban conservarse para acreditar actos contra personas, bienes o instalaciones (art. 22.3)."),
        ("¿Qué es el derecho a la desconexión digital?",
         "El derecho de trabajadores y empleados públicos a que se respete, fuera de su horario, su tiempo de descanso, permisos, vacaciones e intimidad (art. 88.1)."),
    ],
    "ley-2-1998-andalucia": [
        ("¿Qué es el Servicio Andaluz de Salud?",
         "Un organismo autónomo de carácter administrativo de la Junta de Andalucía adscrito a la Consejería de Salud (art. 64.1)."),
        ("¿Puedo elegir médico y centro en Andalucía?",
         "Sí, la ley reconoce el derecho a la libre elección de médico, otros profesionales sanitarios, servicio y centro, en los términos que fije el reglamento (art. 6.1.l)."),
        ("¿Tengo derecho a una segunda opinión médica?",
         "Sí, a una segunda opinión facultativa sobre el propio proceso, en los términos que se establezcan reglamentariamente (art. 6.1.o)."),
    ],
    "leyes-12-13-2007-andalucia": [
        ("¿Qué es la representación equilibrada según la Ley 12/2007?",
         "Que en el conjunto de personas de que se trate cada sexo ni supere el 60 % ni sea menos del 40 % (art. 3.3 de la Ley 12/2007)."),
        ("¿Qué se entiende por violencia de género en la Ley 13/2007?",
         "La que, como consecuencia de una cultura machista y como manifestación de la discriminación y las relaciones de poder de los hombres sobre las mujeres, se ejerce sobre ellas por el hecho de serlo; incluye la violencia vicaria (art. 3.1 de la Ley 13/2007)."),
        ("¿Por qué entra la igualdad en los temarios de la Junta de Andalucía?",
         "Porque la Ley 12/2007 obliga a que los temarios de las pruebas selectivas de la Junta incluyan normativa sobre igualdad y violencia de género (art. 31.1)."),
    ],
    "ley-53-1984": [
        ("¿Puedo tener dos puestos en el sector público?",
         "Por regla general no. Solo en los supuestos de la ley, sobre todo funciones docente y sanitaria, y siempre con autorización previa y expresa de compatibilidad (arts. 1.1 y 3.1)."),
        ("¿Puedo cobrar la pensión de jubilación y trabajar en el sector público?",
         "No: es incompatible y la pensión queda en suspenso mientras se desempeña el puesto. Excepción: la jubilación parcial con un puesto a tiempo parcial en el ámbito laboral (art. 3.2)."),
        ("¿Se puede tener una actividad privada siendo empleado público?",
         "Solo si no impide o menoscaba el estricto cumplimiento de los deberes ni compromete la imparcialidad o independencia, y en los términos de la ley (art. 1.3)."),
    ],
    "ley-39-2015": [
        ("¿Cuál es el plazo para resolver si la norma no dice nada?",
         "Tres meses (art. 21.3)."),
        ("¿Qué pasa si la Administración no contesta a mi solicitud?",
         "Por regla general, en los procedimientos iniciados a solicitud del interesado el silencio es estimatorio, salvo las excepciones de la ley, como el derecho de petición o los recursos (art. 24.1)."),
        ("¿Qué plazo hay para el recurso de alzada y el de reposición?",
         "Un mes en ambos si el acto es expreso. La alzada se resuelve en tres meses y la reposición en un mes (arts. 122 y 124)."),
    ],
    "ley-40-2015": [
        ("¿Qué quórum necesita un órgano colegiado para constituirse?",
         "La asistencia, presencial o a distancia, del Presidente y del Secretario (o sus suplentes) y de la mitad, al menos, de sus miembros (art. 17.2)."),
        ("¿Qué es la abstención?",
         "La obligación de autoridades y personal de no intervenir en un procedimiento cuando se da alguna de las causas de la ley, comunicándolo a su superior inmediato (art. 23.1)."),
        ("¿Cuánto puede durar un convenio administrativo?",
         "Como máximo cuatro años, salvo que una norma prevea más, prorrogables por unanimidad hasta otros cuatro (art. 49.h)."),
    ],
    "constitucion-espanola": [
        ("¿Cuántos artículos y títulos tiene la Constitución?",
         "169 artículos, organizados en un Título preliminar y diez títulos, además de las disposiciones adicionales, transitorias, derogatoria y final."),
        ("¿Qué derechos se pueden defender con el recurso de amparo?",
         "El de igualdad del art. 14, los de la Sección primera del Capítulo segundo del Título I y la objeción de conciencia del art. 30 (art. 53.2)."),
        ("¿Cómo se reforma la Constitución?",
         "Por la vía ordinaria, con tres quintos de cada Cámara (art. 167). Para una revisión total o de partes esenciales hacen falta dos tercios, disolución de las Cortes, nueva aprobación y referéndum (art. 168)."),
    ],
    "trebep": [
        ("¿Qué clases de empleados públicos hay?",
         "Funcionarios de carrera, funcionarios interinos, personal laboral (fijo, por tiempo indefinido o temporal) y personal eventual (art. 8.2)."),
        ("¿Cuántos días de vacaciones y de asuntos particulares tiene un funcionario?",
         "22 días hábiles de vacaciones al año (los sábados no cuentan como hábiles) y seis días de asuntos particulares (arts. 50.1 y 48.k)."),
        ("¿Qué titulación se pide en cada grupo de funcionarios?",
         "A1 y A2: Grado universitario; B: Técnico Superior; C1: Bachiller o Técnico; C2: Graduado en ESO (art. 76)."),
    ],
}


# Texto consolidado en el BOE de cada ley (el mismo que actualizaciones.LEYES_BOE; para leyes con dos textos, el primero)
BOE_IDS = {
    "ley-55-2003": "BOE-A-2003-23101", "ley-41-2002": "BOE-A-2002-22188", "ley-14-1986": "BOE-A-1986-10499",
    "ley-44-2003": "BOE-A-2003-21340", "ley-16-2003": "BOE-A-2003-10715", "ley-31-1995": "BOE-A-1995-24292",
    "lo-3-2007": "BOE-A-2007-6115", "lo-3-2018": "BOE-A-2018-16673", "ley-2-1998-andalucia": "BOE-A-1998-18720",
    "leyes-12-13-2007-andalucia": "BOE-A-2008-2492", "ley-53-1984": "BOE-A-1985-151",
    "ley-39-2015": "BOE-A-2015-10565", "ley-40-2015": "BOE-A-2015-10566",
    "constitucion-espanola": "BOE-A-1978-31229", "trebep": "BOE-A-2015-11719",
}


def enlace_boe(slug, respuesta):
    """URL del primer artículo citado en la respuesta («art. 8.2», «arts. 50.1 y 48.k»), o None si no cita ninguno."""
    m = re.search(r"\barts?\. (\d+)", respuesta)
    if not m or slug not in BOE_IDS:
        return None
    return f"https://www.boe.es/buscar/act.php?id={BOE_IDS[slug]}#a{m.group(1)}", m.group(1)
