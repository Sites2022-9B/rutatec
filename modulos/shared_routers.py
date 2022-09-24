import os
from db import database
from typing import Tuple
from fastapi import APIRouter, Request, Depends
from modulos.personal.models import GrupoTag
from modulos.seguridad.models import *

from modulos.seguridad.r_authentication import SessionData, validarSessionforApis, test_session
from modulos.shared_defs import getAnioFiscalList, getFilePlantilla, getSettingsName, raiseExceptionDataErr, raiseExceptionNoAuth
from fastapi.responses import FileResponse
# import xlsxwriter
import pandas as pd
import xlsxwriter

router = APIRouter( tags=['Routers compartidos'] )

@router.get("/api/templatedata/{catalogo}")
async def apiTemplateData(request:Request, catalogo:str, session: Tuple[SessionData, str] = Depends(test_session), db: Session = Depends(database.get_db)):
    url = '/api/templatedata/'
    userAutentificado = await validarSessionforApis(session=session, db=db)
    if( userAutentificado ):
        dataPlantillaUser = {}
        if (catalogo=="users"): dataPlantillaUser = await User().getStructureTable(database)
        return {dataPlantillaUser}
    raiseExceptionNoAuth(f"Acceso no autorizado")

#  para crear y descargar las plantillas
@router.get("/api/templatefile/{cat}")
async def apiTemplateFile(request:Request, cat:str, ret: str = "/main", session: Tuple[SessionData, str] = Depends(test_session), db: Session = Depends(database.get_db)):
    url = '/api/templatefile'
    userAutentificado = await validarSessionforApis(session=session, db=db)
    if( userAutentificado ):
        estructura = []
        rutaPlantilla = ""
        nombArchivo = ""
        rutaDePlantillas = getSettingsName("$SYS_DIR_MODELS_PLANTILLAS", "/f/models_plantillas")
        arrModulosDisponibles = ["usuarios", "roles", "empleados", "puestos", "areas", "estadosmunicipios", "municipiolocalidades","ctabancaria"
            ,"ctabancariamovs", "tipoComisión", "requni", "tabulador", "pptoaportipo", "capitulosypartidas", "pidemeta", "grupotag","planprog", 
            "Pptostatus"]
        if (cat in arrModulosDisponibles): 
            if cat == "usuarios": estructura = [{"nombreHoja": cat, "columnas":["full_name", "email", "password"], "datos":None}]
            if cat == "roles": estructura =  [{"nombreHoja": cat, "columnas":["rol"], "datos":None}]
            if cat == "empleados": estructura =  [{"nombreHoja": cat, "columnas":["codigo", "nombre","apepat", "apemat", "sexo", "nss", "curp", "rfc", "telefono", "domicilio"], "datos":None}]
            if cat == "areas": estructura =  [{"nombreHoja": cat, "columnas":["codigo", "nombre"], "datos":None}]               
            if cat == "estadosmunicipios": 
                estados = db.query(Comedo.id, Comedo.estado).all()
                estructura =  [{"nombreHoja": cat, "columnas":["comedo_id", "municipio", "codigo_mun", "zona"], "datos":None},
                {"nombreHoja": "Estados de la republica", "columnas":["Id", "Estados"], "datos":estados}]        
            if cat == "municipiolocalidades": 
                municipio = db.query(ComedommunicipioGetVw.id, ComedommunicipioGetVw.estado, ComedommunicipioGetVw.municipio).all()
                estructura =  [{"nombreHoja": cat, "columnas":["comedomunicipio_id", "localidad"], "datos":None},
                {"nombreHoja": "Municipios existentes", "columnas":["Comedomunicipio_id", "Estados", "Municipios"], "datos":municipio}]       
            if cat == "ctabancaria": estructura =  [{"nombreHoja": cat, "columnas":["banco", "cuenta","clabe", "fechaini", "fechafin", "descripcion"], "datos":None}]
            if cat == "ctabancariamovs": estructura =  [{"nombreHoja": cat, "columnas":["fecha","folio", "descr_referencia", "monto", "saldo"], "datos":None}]
            if cat == "puestos":
                datosgTag = db.query(GrupoTag.id, GrupoTag.grupo, GrupoTag.nombre).all()
                estructura =  [{"nombreHoja": cat, "columnas":["clave", "nombre", "grupotag_id"], "datos":None},
                                {"nombreHoja": "grupoTag", "columnas":["id", "grupo", "nombre"], "datos":datosgTag}]
            if cat == "tipoComisión": estructura =  [{"nombreHoja": cat, "columnas":["tipo"], "datos":None}]
            if cat == "requni": 
                tramites = db.query(Tramite.id, Tramite.tramite).all()
                estructura = [{"nombreHoja": cat, "columnas":["unidadmed", "descripcion", "tramite_id"], "datos":None},
                                {"nombreHoja": "Trámites", "columnas":["id", "tramite"], "datos":tramites}]
            if cat == "pptoaportipo": estructura =  [{"nombreHoja": cat, "columnas":["aportacion"], "datos":None}]       
            
            if cat == "tabulador": estructura =  [{"nombreHoja": cat, "columnas":["nivel", "zona1full","zona2full", "zona3full", "zona4full", "zona1tran", "zona2tran", "zona3tran", "zona4tran"], "datos":None}]
            if cat == "capitulosypartidas": estructura =  [{"nombreHoja": cat, "columnas":["partida", "concepto"], "datos":None}]

            if cat == "pidemeta": 
                datosunimedida = db.query(Requni.id, Requni.unidadmed,Requni.descripcion).all()
                datosPlanProg = db.query(PlanProg.id, PlanProg.programa).all()
                estructura =  [{"nombreHoja": cat,"columnas":["indicador", "formula", "actividades", "cantidad", "metashort", "acumulativos", "año1", "año2", "año3", "año4", "año5", "año6", "año7","año8","año9","año10","planprog_id","unimedida_id","metanacional","areasresponsables"], "datos":None},
                {"nombreHoja": "unidad de medida", "columnas":["Id", "Abreviación","Descripción"], "datos":datosunimedida},
                {"nombreHoja": "Planprog", "columnas":["Id","Programa"], "datos":datosPlanProg}]
            if cat == "grupotag": estructura =  [{"nombreHoja": cat, "columnas":["grupo", "nombre"], "datos":None}] 
            if cat == "Pptostatus": estructura =  [{"nombreHoja": cat, "columnas":["estatus"], "datos":None}]
            
            if cat == "planprog": estructura = [{"nombreHoja":cat, "columnas":["programa","estructura"],"datos":None}]
            rutaPlantilla = await getFilePlantilla(cat, rutaDePlantillas, estructura)
            return FileResponse(path=rutaPlantilla)
        else:
            raiseExceptionDataErr(f"La plantilla [{cat}] no está disponible!!!, consultelo con el administrador del sistema")
    raiseExceptionNoAuth(f"Acceso no autorizado")

# para descargar la observaciones de los archivos excel
@router.get("/api/templateuploads/{file_name}")
async def apiUserTemplateFile(request:Request, file_name:str, session: Tuple[SessionData, str] = Depends(test_session), db: Session = Depends(database.get_db)):
    url = '/api/templateuploads'
    userAutentificado = await validarSessionforApis(session=session, db=db)
    if( userAutentificado ):
        rutaDePlantillasUploads = getSettingsName("$SYS_DIR_MODELS_PLANTILLAS_UPLOADS", "/f/models_plantillas_uploads")
        rutafile=f"{os.getcwd()}{rutaDePlantillasUploads}/{file_name}"
        return FileResponse(path=rutafile, filename= f"{file_name}")
    raiseExceptionNoAuth(f"Acceso no autorizado")

@router.get("/api/aniofiscal/combo")
async def getAreasCombo(q:str="", q_aniofiscal_id:str="", session: Tuple[SessionData, str] = Depends(test_session), db: Session = Depends(database.get_db)):
    url = '/api/aniofiscal/combo'
    userAutentificado = await validarSessionforApis(session=session, db=db)
    if( userAutentificado ):
        metadata = ["id", "anio"]
        rows = getAnioFiscalList()
        if ( len(q_aniofiscal_id)>0 ) : 
            for key,val in rows:
                if q_aniofiscal_id == str(key):
                    rows = [[key, val]]
                    break
        return {'metadata': metadata, 'data': rows}
    raiseExceptionNoAuth(f"Acceso no autorizado")

@router.get('/api/histramite/{procexec_id}')
async def getHistTramite(request:Request, procexec_id: int, session: Tuple[SessionData, str] = Depends(test_session), db: Session = Depends(database.get_db)):
    userAutentificado = await validarSessionforApis(session=session, db=db)
    if( userAutentificado ):
        sql = f'''
            SELECT pact.id, pact.porcavance as porcentaje, pact.statusdocto as statusdoctoxec, pa.actividad, u.full_name || ' - ' || r.rol as participante, pact.fechaatencion as fechaatencion, pact.fechaatendida as fechaatendida, pact.status
            FROM(
                SELECT * FROM procexec where id = {procexec_id}
            )pe	
            LEFT JOIN procact pa ON pe.proc_id  = pa.proc_id   
            LEFT JOIN procactexec pact ON pa.id = pact.procact_id and pe.id = pact.procexec_id
            LEFT JOIN "user" u ON u.id = pact.user_id
            LEFT JOIN procactrol pr ON pr.procact_id = pa.id
            LEFT JOIN rol r ON r.id = pr.rol_id
        '''
        # Obtener la página de registros derivados de la consulta
        getTotal = True
        [metadata, rows, total] = database.execSql(sql, {}, False, True, getTotal)
        labels = ['Id','Porcentaje', 'statusdocto', 'actividad', 'participante', 'fechaatencion', 'fechaatendida', 'status', 'tiempo']
        return {"labels":labels, "metadata" : metadata, "data": rows, "total" : total}
    raiseExceptionNoAuth(f"Acceso no autorizado")


@router.get('/api/hisactividad/{procactexec_id}')
async def getHistTramite(request:Request, procactexec_id: int, session: Tuple[SessionData, str] = Depends(test_session), db: Session = Depends(database.get_db)):
    userAutentificado = await validarSessionforApis(session=session, db=db)
    if( userAutentificado ):
        sql = f'''
            select pax.id, pax.user_id, pax.procact_id, pax.fechaasignacion, pax.fechaatencion, pax.fechaatendida, pax.fechareasignacion, pax.fechacancelacion, pax.status, pax.statusdocto, uant.full_name AS envio, us.full_name as usuarioActual
            from(
                select pax.procact_id, pax.procexec_id from procactexec as pax where pax.id = {procactexec_id}
            )as objpax
            LEFT JOIN procactexec as pax on pax.procact_id = objpax.procact_id AND pax.procexec_id = objpax.procexec_id
            LEFT JOIN "user" AS us ON pax.user_id = us.id
            LEFT JOIN "user" AS uant ON pax.userant_id = uant.id
        '''
        # Obtener la página de registros derivados de la consulta fechacancelacion, fechareasignacion
        getTotal = True
        [metadata, rows, total] = database.execSql(sql, {}, False, True, getTotal)
        labels = ['Id','User ID', 'Procact id', 'Fecha Asignación', 'Fecha Atención', 'Fecha Atendida', 'Status', 'Status Docto', 'De', 'Para']
        return {"labels":labels, "metadata" : metadata, "data": rows, "total" : total}
    raiseExceptionNoAuth(f"Acceso no autorizado")

@router.get('/api/observaciones/{procexec_id}')
async def getObservacione(request:Request, procexec_id: int, session: Tuple[SessionData, str] = Depends(test_session), db: Session = Depends(database.get_db)):
    userAutentificado = await validarSessionforApis(session=session, db=db)
    if( userAutentificado ):
        sql = f''' SELECT observaciones FROM procexec WHERE id = {procexec_id}'''
        # Obtener la página de registros derivados de la consulta
        getTotal = True
        [metadata, observacion, total] = database.execSql(sql, {}, False, True, getTotal)
        print(observacion)
        return {"metadata" : metadata, "data": observacion, "total" : total}
    raiseExceptionNoAuth(f"Acceso no autorizado")

@router.get("/api/ReporteExcelProy")
async def apiReporteExcelProy(request:Request, ret: str = "/main", session: Tuple[SessionData, str] = Depends(test_session), db: Session = Depends(database.get_db)):
    url = '/api/templatefile'
    # userAutentificado = await validarSessionforApis(session=session, db=db)
    if( True ):
        sql =f''' 
            Select pr.id, pr.codigo, pr.proyecto, pr.numproceso, 
                patp.tipoproc, 
                CASE 
                    WHEN pr.planprog_id = 1 THEN 'EQUIDAD'
                    WHEN pr.planprog_id = 2 THEN 'ACADÉMICO'
                    WHEN pr.planprog_id = 3 THEN 'VINCULACIÓN'
                    WHEN pr.planprog_id = 4 THEN 'GESTIÓN'
                END, 
                pr.fechaini, pr.fechafin, emp.titulo || ' ' || emp.nombre ||' '|| emp.apepat ||' '|| emp.apemat rector , pr.objetivo, pr.problematica, pr.alcance, em.titulo || ' ' || em.nombre ||' '|| em.apepat ||' '|| em.apemat as responsablearea From
                (SELECT id, codigo, proyecto, numproceso, poatipoproc_id, planprog_id, to_char(fechaini, 'DD/MM/YYYY') fechaini, to_char(fechafin, 'DD/MM/YYYY') fechafin, rector_id, objetivo, problematica, alcance
                FROM proy Where id =1) pr
                Left Join poatipoproc patp on patp.id = pr.poatipoproc_id
                Left Join arearesponsable ares on ares.id = pr.rector_id 
                Left Join empleados emp on emp.id = ares.empleado_id
                LEFT JOIN procexecproy pxpr on pxpr.proy_id = pr.id 
                LEFT JOIN procexec px on px.id = pxpr.procexec_id
                LEFT JOIN areas ar on ar.id = px.area_id
                left join arearesponsable arp on ar.id = arp.area_id  and px.aniofiscal BETWEEN EXTRACT(Year From arp.fechaini) and coalesce (EXTRACT(Year From arp.fechafin),  EXTRACT(Year From date(now()+ '1000 day')))
                Left Join empleados em on em.id = arp.empleado_id
        '''
        [metadata, datosProy] = database.execSql(sql, {}, False, True)
        # print("datos del proy", datosProy[0])

        if len(datosProy)==0:
                    datosProy =[["","","","","","","","","","","",""]]

        sql2=f''' 
            SELECT p.id, pm.metashort, p.cantidadactual, p.cantidadactualporc, p.fechaactual, p.cantidadplan, 
                p.cantidadplanporc, p.fechaplan, p.cantidadobtenida, p.cantidadobtenidaporc, p.fechaobtenida
                FROM (
                    SELECT * FROM proymeta WHERE proy_id = 1)p 
                    JOIN pidemeta pm ON pm.id = p.pidemeta_id 
                    LEFT JOIN proyact pa on pa.proymeta_id = p.id 
            '''
        [metadata, indicadores] = database.execSql(sql2, {}, False, True)
        print("datos de los indicadores", indicadores[0])
        if len(indicadores)==0:
                    indicadores =[["","","","","","","","","","",""]]

        sql3=f''' 
            SELECT pa.id, pim.metashort as indicador, pa.actividad, u.descripcion,ar.nombre,  pa.metanual FROM 
                    ( SELECT * FROM proyact WHERE proy_id = 1)pa
                    LEFT JOIN proyactcalendario pac ON pac.proyact_id = pa.id
                    LEFT JOIN unimedida u ON u.id = pa.unimedid_id
                    LEFT JOIN areas ar ON ar.id = pa.responsableact
                    LEFT JOIN proymeta prm ON prm.id = pa.proymeta_id
                    LEFT JOIN pidemeta pim ON pim.id = prm.pidemeta_id 
            '''
        [metadata, actividades] = database.execSql(sql3, {}, False, True)
        # print("datos de los actividades", actividades[0])
        if len(actividades)==0:
                    actividades=[["","","","","",""]]

        sql4=f''' 
            SELECT pa.id, pa.fechaplan||'' fechaplan, pa.numprog, pa.porcenprog, pa.numalc, pa.porcenalc FROM 
                ( SELECT * FROM proyactcalendario WHERE proyact_id = {actividades[0][0]})pa
            '''
        [metadata, calendario] = database.execSql(sql4, {}, False, True)
        # print("datos de los calendarios", calendario[0])
        if len(calendario)==0:
                    calendario=[["","","","","",""]]


    with xlsxwriter.Workbook(f'f/reportes_plantillas/reporteProys.xlsx') as workbook:
        

        # Formato de titulo
        titulo = workbook.add_format({
            'bold': 1,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'fg_color': '#333f4f',
            'font_color': 'white',
            'text_wrap': True
            
        })
        subtitulo = workbook.add_format({
            'bold': 1,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'fg_color': '#FF5733',
            'font_color': 'white',
            'text_wrap': True
            
        })
        # Formato de variables
        variables = workbook.add_format({
            'bold': 1,
            'border': 1,
            'align': 'left',
            'valign': 'top',
            'fg_color': '#ddebf7',
            'font_color': 'black',
            'text_wrap': True,
        })
        # Formato del texto normal
        normal = workbook.add_format({
            'border': 1,
            'align': 'left',
            'valign': 'top',
            'text_wrap': True})


        worksheet = workbook.add_worksheet("PROYECTO POA")
        
        
        if True == False :
            worksheet.set_column('B:B', 40)
            worksheet.set_column('C:C', 20)
            worksheet.set_column('D:D', 25)
            worksheet.set_column('E:E', 50)

            # Cambiamos tamaños de filas
            worksheet.set_row(0, 40)
            # primer tab 
            worksheet.set_row(1, 30)
            worksheet.set_row(2, 30)
            worksheet.set_row(3, 30)
            worksheet.set_row(4, 30)
            worksheet.set_row(5, 30)
            worksheet.set_row(6, 30)
            worksheet.set_row(7, 30)
            worksheet.set_row(8, 30)
            worksheet.set_row(9, 30)
            worksheet.set_row(10, 30)
            worksheet.set_row(11, 30)
            worksheet.set_row(12, 30)
            worksheet.set_row(13, 30)
            # Tab de indicadores
            worksheet.set_row(14, 40)

            worksheet.set_row(15, 30)
            worksheet.set_row(16, 30)
            worksheet.set_row(17, 30)
            worksheet.set_row(18, 30)
            worksheet.set_row(19, 30)
            worksheet.set_row(20, 30)
            worksheet.set_row(21, 30)
            worksheet.set_row(22, 30)
            worksheet.set_row(23, 30)
            worksheet.set_row(24, 30)


        worksheet.merge_range('B1:E1', 'Reporte de proyectos',titulo)
        # CAMPOS DE REPORTE
        worksheet.write('B2', 'Código', variables)
        worksheet.write('B3', 'Proyecto', variables)
        worksheet.write('B4', 'Tipo Proyecto', variables)
        worksheet.write('B5', 'Num. Proceso', variables)
        worksheet.write('B6', 'Tipo Proceso', variables)
        worksheet.write('B7', 'Tipo programa', variables)
        worksheet.write('B8', 'Fecha de inicio',variables)
        worksheet.write('B9', 'Fecha de Fin',variables)
        worksheet.write('B10', 'Rector',variables)
        worksheet.write('B11', 'Objetivo',variables)
        worksheet.write('B12', 'Problemática',variables)
        worksheet.write('B13', 'Alcance',variables)
        worksheet.write('B14', 'Responsable de proyecto',variables)

        # VALORES DE CAMPOS
        worksheet.merge_range('C2:E2', datosProy[0][1], normal)
        worksheet.merge_range('C3:E3', datosProy[0][2], normal)
        worksheet.merge_range('C4:E4', 'POA', normal)
        worksheet.merge_range('C5:E5', datosProy[0][3], normal)
        worksheet.merge_range('C6:E6', datosProy[0][4], normal)
        worksheet.merge_range('C7:E7', datosProy[0][5],normal)
        worksheet.merge_range('C8:E8', datosProy[0][6],normal)
        worksheet.merge_range('C9:E9', datosProy[0][7],normal)
        worksheet.merge_range('C10:E10', datosProy[0][8],normal)
        worksheet.merge_range('C11:E11', datosProy[0][9],normal)
        worksheet.merge_range('C12:E12', datosProy[0][10],normal)
        worksheet.merge_range('C13:E13', datosProy[0][11],normal)
        worksheet.merge_range('C14:E14', datosProy[0][12],normal)




        worksheet2 = workbook.add_worksheet("INDICADORES")
        worksheet2.write('A1', 'ID', variables)
        worksheet2.write('B1', 'Indicador', variables)
        worksheet2.write('C1', 'Cant. Actual', variables)
        worksheet2.write('D1', '% Cant. Actual', variables)
        worksheet2.write('E1', 'Fecha Actual',variables)
        worksheet2.write('F1', 'Cant. Planeada', variables)
        worksheet2.write('G1', '% Cant. Planeada', variables)
        worksheet2.write('H1', 'Fecha Planeada', variables)
        worksheet2.write('I1', 'Cant. Alcanzada',variables)
        worksheet2.write('J1', '% Cant. Alcanzada', variables)
        worksheet2.write('K1', 'Fecha Alcanzada',variables)
        contadorind = 1
        for i in indicadores:
            contadorind += 1 
            indfila = str(contadorind)
            # Valores de indicadores
            worksheet2.write('A'+indfila, i[0], normal)
            worksheet2.write('B'+indfila, i[1], normal)
            worksheet2.write('C'+indfila, i[2], normal)
            worksheet2.write('D'+indfila, i[3], normal)
            worksheet2.write('E'+indfila, i[4], normal)
            worksheet2.write('F'+indfila, i[5], normal)
            worksheet2.write('G'+indfila, i[6], normal)
            worksheet2.write('H'+indfila, i[7], normal)
            worksheet2.write('I'+indfila, i[8], normal)
            worksheet2.write('J'+indfila, i[9], normal)
            worksheet2.write('K'+indfila, i[10], normal)



        worksheet3 = workbook.add_worksheet("ACTIVIDADES")
        worksheet3.merge_range('A1:F1', 'ACTIVIDADES', subtitulo)

        worksheet3.write('A2', 'ID', variables)
        worksheet3.write('B2', 'Indicador', variables)
        worksheet3.write('C2', 'Actividad', variables)
        worksheet3.write('D2', 'Descripción',variables)
        worksheet3.write('E2', 'Area ejecutora', variables)
        worksheet3.write('F2', 'Meta anual', variables)
        actcont=2
        print( 'cantidad de actividades',array.count(actividades))
        for j in actividades:
            actcont+=1
            actfila=str(actcont)
            print('activid',actividades)
            worksheet3.write('A'+actfila, j[0], normal)
            worksheet3.write('B'+actfila, j[1], normal)
            worksheet3.write('C'+actfila, j[2], normal)
            worksheet3.write('D'+actfila, j[3], normal)
            worksheet3.write('E'+actfila, j[4], normal)
            worksheet3.write('F'+actfila, j[5], normal)
            
            worksheet3.merge_range('G1:L1', 'ACTIVIDADES CALENDARIZADAS', subtitulo)

            worksheet3.write('G2', 'ID',variables)
            worksheet3.write('H2', 'Fecha de revisión de la actividad',variables)
            worksheet3.write('I2', 'Cant. Planeada', variables)
            worksheet3.write('J2', 'Porcentaje planeado',variables)
            worksheet3.write('K2', 'Cant. Alcanzada',variables)
            worksheet3.write('L2', 'Porcentaje alcanzado', variables)

            for k in calendario:
                calcon=actcont
                fila2=str(calcon)

                worksheet3.write('G'+fila2, k[0],normal)
                worksheet3.write('H'+fila2, k[1],normal)
                worksheet3.write('I'+fila2, k[2], normal)
                worksheet3.write('J'+fila2, k[3],normal)
                worksheet3.write('K'+fila2, k[4],normal)
                worksheet3.write('L'+fila2, k[5], normal)
                actcont+=1


        


    workbook.close()


    # raiseExceptionDataErr(f"La plantilla no está disponible!!!, consultelo con el administrador del sistema")