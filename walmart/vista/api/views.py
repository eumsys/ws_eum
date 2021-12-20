from django.shortcuts import render
from transaccion.models import Transaccion, Tienda, Boleto
from equipo.models import Equipo
from datetime import datetime, timezone, timedelta

from django.db.models import Sum, Q, Count
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework.views import APIView
from django.views.generic.list import ListView
from .Calculador import Calculador
from django.utils.timezone import now
import random
import pytz
#Vista consultarTransaccion2
from rest_framework import serializers
from .serializers import  BoletoSerializer, TransaccionSerializer

# Create your views here.
tiempo_tolerancia = 15
no_proveedor = 2
class CorteApiView(APIView):
    """
    A view that returns the count of active users in JSON.
    """
    renderer_classes = [JSONRenderer]
    def get(self, request, format=None):
        fecha_1 = self.request.GET.get('f1')
        hora_1 = self.request.GET.get('h1')
        fecha_2 = self.request.GET.get('f2')
        hora_2 = self.request.GET.get('h2')
        fechahora_1 = datetime.strptime(str(fecha_1)+" "+str(hora_1), '%d-%m-%Y %H:%M:%S')
        fechahora_2 = datetime.strptime(str(fecha_2)+" "+str(hora_2), '%d-%m-%Y %H:%M:%S')
        exitosos = 0
        incidencias = 0
        cancelados = 0
        ingreso = 0
        operaciones = 0
        print("datetimes:",fechahora_1,fechahora_2)
        if fechahora_1:
            if fechahora_2:
                transaccion = Transaccion.objects.filter(created__range=[fechahora_1, fechahora_2])
                exitosos = transaccion.filter(codigo = 1).count()
                incidencias = transaccion.filter(codigo__range=(2, 4)).count()
                cancelados = transaccion.filter(codigo = 5).count()
                ingreso=transaccion.aggregate(Sum('monto'))['monto__sum']
                operaciones = transaccion.count()
                print("Transaccion full: ",transaccion)
            else:
                transaccion = Transaccion.objects.filter(
                    Q(created__date=fechahora_1)
                    )
                return transaccion
        else:
            transaccion = Transaccion.objects.all()

        print(ingreso)
        print("pagos: ", operaciones)

        content = {
            'operaciones': operaciones,
            'ingreso': ingreso,
            'exitosos':exitosos,
            'incidencias':incidencias,
            'cancelados':cancelados
            }
        return Response(content)


class consultaBoletoApiView(APIView):
    """
    A view that returns the count of active users in JSON.
    """
    #Ejemplo : http://127.0.0.1:8000/api/consultaBoleto/?idboleto=12050821140000557201&te=001&tr=0001&tda=5572
    renderer_classes = [JSONRenderer]
    def post(self, request, format=None):
        #idBoleto = self.request.GET.get('idboleto')
        idBoleto = self.request.data.get('consultaBoletoRequest').get('idBoleto')
        te = self.request.data.get('consultaBoletoRequest').get('te')
        tr = self.request.data.get('consultaBoletoRequest').get('tr')
        tda = self.request.data.get('consultaBoletoRequest').get('tda')
        #idBoleto2 = self.request.data.get('consultaBoletoRequest').get('idBoleto')
        #print("idboleto222", idBoleto2)
        exitosos = 0
        incidencias = 0
        cancelados = 0
        ingreso = 0
        operaciones = 0
        print("idBoleto:  , tienda: ",idBoleto,tda)
        #print("Proveedor: ",idBoleto[0:2])
        #print("Dia: ",idBoleto[2:4])
        calculador = Calculador()
        try:
            print (len(idBoleto))
            if len(idBoleto) == 20:
                proovedor = idBoleto[0:2]
                if int(proovedor) == no_proveedor:
                    pass
                else:
                    content = {
                    "consultaBoleto": {
                    "idBoleto": idBoleto,
                    "impresionPantalla": "Gracias por su compra",
                    "impresionTicket": "Compre Walmart",
                    "codRepuesta": "01",
                    "codigoError": "02",
                    "descripcionError": "BOLETO NO VALIDO",
                    "numAutorizacion": ""
                    }
                    }
                    print("Proveedor invalido:",idBoleto)
                    return Response(content)
            else:
                content = {
                "consultaBoleto": {
                "idBoleto": idBoleto,
                "impresionPantalla": "Gracias por su compra",
                "impresionTicket": "Compre Walmart",
                "codRepuesta": "01",
                "codigoError": "02",
                "descripcionError": "BOLETO NO VALIDO",
                "numAutorizacion": ""
                }
                }
                print("Longitud de id incorrecta:",idBoleto)
                return Response(content)


            tienda = Tienda.objects.filter(id_tienda=tda,activo=True)
            print("Tienda:",tienda)
            det_estacionamiento = idBoleto[14:18]
            if (tienda and (tda == str(det_estacionamiento))):
                pass
            else:
                content = {
                "consultaBoleto": {
                "idBoleto": "",
                "impresionPantalla": "Gracias por su compra",
                "impresionTicket": "Compre Walmart",
                "monto": "",
                "codRepuesta": "01",
                "codigoError": "04",
                "descripcionError": "COBRO NO HABILITADO PARA ESTA TIENDA",
                "numAutorizacion": ""
                }
                }
                return Response(content)


            #Obtener datos
            proovedor = idBoleto[0:2]
            mes_boleto = idBoleto[2:4]
            dia_boleto = idBoleto[4:6]
            anio_boleto = idBoleto[6:8]
            hora_boleto = idBoleto[8:10]
            minuto_boleto = idBoleto[10:12]
            segundo_boleto = idBoleto[12:14]
            det_estacionamiento = idBoleto[14:18]
            entrada = idBoleto[18:20]

            '''
            - Obtener estado del boleto antes de calcular tarifa
            - Estado 1 Sin previo pago: permitir realizar el pago
            - Estado 2 Pagado: Realizar calculo de tiempo a partir del ultimo pago/transaccion registrada
                Nota: Se resuelven dos vistas pendientes en este paso
            - Estado 3 Obsoleto: No permitir el pago
            '''

            fecha_boleto = dia_boleto + "-" + mes_boleto + "-" + anio_boleto
            hora_boleto = hora_boleto + ":" + minuto_boleto + ":" + segundo_boleto
            sec = datetime.strptime("01:00:31", '%H:%M:%S')
            fechahora_boleto = datetime.strptime(str(fecha_boleto)+" "+str(hora_boleto), '%d-%m-%y %H:%M:%S')



            fecha_actual = datetime.now().strftime('%d-%m-%y')
            hora_actual = datetime.now().strftime('%H:%M:%S')
            resultado = calculador.calcular_tarifa(str(fecha_actual),str(hora_actual),str(fecha_boleto),str(hora_boleto),0)

            monto = resultado [0]
            tiempo_estacionado = resultado [1]
            print("fecha_hora: ",fechahora_boleto)
            print("entrada",entrada)

            #transaccion = Transaccion.objects.filter(fecha_expedicion_boleto=fechahora_boleto,expedidor_boleto=entrada)
            if tiempo_estacionado > tiempo_tolerancia:
                pass
            else:
                content = {
                "consultaBoleto": {
                "idBoleto": "",
                "impresionPantalla": "Gracias por su compra",
                "impresionTicket": "Compre Walmart",
                "monto": "",
                "codRepuesta": "01",
                "codigoError": "03",
                "descripcionError": "Boleto con tiempo de tolerancia vigente ({} MIN)".format(tiempo_tolerancia-tiempo_estacionado),
                "numAutorizacion": ""
                }
                }
                return Response(content)



            boleto = Boleto.objects.filter(fecha_expedicion_boleto=fechahora_boleto,entrada=entrada)


            if boleto:

                estado = boleto[0].estado
                folio_boleto = boleto[0].id

                if estado == 1:
                    #Actualiza la hora de consulta en el campo update
                    print(datetime.today(),type(str(datetime.today())),fechahora_boleto)
                    Boleto.objects.filter(fecha_expedicion_boleto=fechahora_boleto,entrada=entrada).update(updated=str(datetime.today()))

                    """fa = datetime.now().strftime('%Y-%m-%d')
                    ha = datetime.now().strftime('%H:%M:%S')
                    fechahora_actual = datetime.strptime(fa + " " + ha , '%Y-%m-%d %H:%M:%S')
                    print("fechahora_actual",fechahora_actual)
                    fecha_actual = datetime.now().strftime('%d/%m/%y')
                    hora_actual = datetime.now().strftime('%H:%M')
                    print("Hora y fecha actual:", fecha_actual, hora_actual)

                    fechahora_actual = datetime.now().strftime('%d-%m-%y %H:%M:%S')
                    utc_dt = pytz.timezone ("America/Mexico_City").localize(datetime.strptime (fechahora_actual, "%d-%m-%y %H:%M:%S"), is_dst=None).astimezone(pytz.utc)
                    f = utc_dt.strftime ("%d-%m-%y %H:%M:%S")
                    print(utc_dt)
                    Boleto.objects.filter(fecha_expedicion_boleto=fechahora_boleto,entrada=entrada).update(updated=utc_dt)
                    """


                elif estado == 2:
                    transacciones = Transaccion.objects.filter(folio_boleto=folio_boleto)
                    print("Transacciones:", transacciones)
                    pass

                elif estado == 3:
                    content = {
                    "consultaBoleto": {
                    "idBoleto": idBoleto,
                    "impresionPantalla": "Gracias por su compra",
                    "impresionTicket": "Compre Walmart",
                    "codRepuesta": "01",
                    "codigoError": "02",
                    "descripcionError": "BOLETO NO VALIDO",
                    "numAutorizacion": ""
                    }
                    }
                    print("Boleto obsoleto:",idBoleto)
                    return Response(content)


                print("Se encontro:",boleto)
                print("Folio Boletoo:", boleto[0].folio_boleto,boleto[0].id)

                #print("Monto: ", boleto[0].monto)
                #monto = boleto[0].monto
                #codigo = boleto[0].codigo
                content = {
                    'consultaBoleto':{
                    'idBoleto': idBoleto,
                    'impresionPantalla': "Gracias por su compra",
                    'impresionTicket': "Compre Walmart",
                    'monto': "{:.2f}".format(float(monto)),
                    'codRepuesta': "00",
                    'codigoError': "00",
                    'descripcionError': "",
                    'numAutorizacion': ""
                    }
                }
            else:
                content = {
                "consultaBoleto": {
                "idBoleto": idBoleto,
                "impresionPantalla": "Gracias por su compra",
                "impresionTicket": "Compre Walmart",
                "codRepuesta": "01",
                "codigoError": "02",
                "descripcionError": "BOLETO NO VALIDO",
                "numAutorizacion": ""
                }

                }
                print("No se encontro:",boleto)
        except: #except
            print("Error al extraer datos")
            content = {
                "consultaBoleto": {
                "idBoleto": idBoleto,
                "impresionPantalla": "Gracias por su compra",
                "impresionTicket": "Compre Walmart",
                "codRepuesta": "01",
                "codigoError": "02",
                "descripcionError": "BOLETO NO VALIDO.",
                "numAutorizacion": ""
                }

                }
        return Response(content)


class registroBoletoApiView(APIView):
    """
    A view that returns the count of active users in JSON.
    """
    #Ejemplo : http://127.0.0.1:8000/api/consultaBoleto/?idboleto=12050821140000557201&te=001&tr=0001&tda=5572
    renderer_classes = [JSONRenderer]
    def post(self, request, format=None):
        #idBoleto = self.request.GET.get('idboleto')
        folio = self.request.data.get('registroBoletoRequest').get('folio')
        entrada = self.request.data.get('registroBoletoRequest').get('entrada')
        fecha_expedicion = self.request.data.get('registroBoletoRequest').get('fecha_expedicion')
        estado = self.request.data.get('registroBoletoRequest').get('estado')
        registrado = self.request.data.get('registroBoletoRequest').get('registrado')
        tda = self.request.data.get('registroBoletoRequest').get('tienda')
        print("folio:  , tienda: ",folio,tda)
        if 1:
            tienda = Tienda.objects.filter(id_tienda=tda,activo=True)
            print("Tienda:",tienda)
            if tienda:
                pass
            else:
                content = {
                'registroBoleto':{
                'idBoleto': folio,
                'codigoError': "04",
                'descripcionError': "Cobro NO habilitado para esta tienda",
                }
                }
                return Response(content)




            fechahora_boleto = datetime.strptime(fecha_expedicion, '%d-%m-%Y %H:%M:%S')


            print("fecha_hora: ",fechahora_boleto)
            print("entrada: ",entrada)

            equipo = Equipo.objects.filter(id=1)
            print(equipo)
            boleto = Boleto.objects.create(
                                                fecha_expedicion_boleto=fechahora_boleto,
                                                folio_boleto=folio,
                                                entrada=entrada,
                                                estado=estado,
                                                registrado=registrado,
                                                equipo_id=equipo[0],
                                                tienda_id=tienda[0],
                                                )

            print(equipo,boleto)
            if boleto:
                print("Se encontro:",boleto)
                #print("Monto: ", boleto[0].monto)
                #monto = boleto[0].monto
                #codigo = boleto[0].codigo
                content = {
                    'registroBoleto':{
                    'codRepuesta': "00",
                    'codigoError': "00",
                    'descripcionError': "Registro exitoso",
                    }
                }
                print("Boleto Registrado: ", boleto)
            else:
                content = {
                'registroBoleto':{
                'idBoleto': idBoleto,
                'codigoError': "02",
                'descripcionError': "Boleto NO valido",
                }

                }
                print("No se encontro:",boleto)
                return Response(content)
        else: #except
            print("Error al extraer datos")
            content = {
                'registroBoleto':{
                'idBoleto': idBoleto,
                'codigoError': "01",
                'descripcionError': "Inconsistencia de datos",
                }

            }
        return Response(content)



class registroTransaccionApiView(APIView):
    """
    A view that returns the count of active users in JSON.
    """
    #Ejemplo : http://127.0.0.1:8000/api/consultaBoleto/?idboleto=12050821140000557201&te=001&tr=0001&tda=5572
    renderer_classes = [JSONRenderer]
    def post(self, request, format=None):
        #idBoleto = self.request.GET.get('idboleto')
        no_provedor = self.request.data.get('registroTransaccion').get('no_provedor')
        det_estacionamiento = self.request.data.get('registroTransaccion').get('det_estacionamiento')
        folio_boleto = self.request.data.get('registroTransaccion').get('folio_boleto')
        entrada = self.request.data.get('registroTransaccion').get('entrada')
        fecha_expedicion = self.request.data.get('registroTransaccion').get('fecha_expedicion')
        fecha_pago = self.request.data.get('registroTransaccion').get('fecha_pago')
        codigo = self.request.data.get('registroTransaccion').get('codigo')
        registrado = self.request.data.get('registroTransaccion').get('registrado')
        tda = self.request.data.get('registroTransaccion').get('tienda')
        monto = self.request.data.get('registroTransaccion').get('monto')
        cambio = self.request.data.get('registroTransaccion').get('cambio')
        monedas = self.request.data.get('registroTransaccion').get('monedas')
        billetes = self.request.data.get('registroTransaccion').get('billetes')
        cambio_entregado = self.request.data.get('registroTransaccion').get('cambio_entregado')
        print("folio:  , tienda: ",folio_boleto,tda)
        if 1:
            tienda = Tienda.objects.filter(id_tienda=tda,activo=True)
            print("Tienda:",tienda)
            if tienda:
                pass
            else:
                content = {
                'registroBoleto':{
                'idBoleto': folio_boleto,
                'codigoError': "04",
                'descripcionError': "Cobro NO habilitado para esta tienda",
                }
                }
                return Response(content)

            fechahora_pago = datetime.strptime(fecha_pago, '%d-%m-%Y %H:%M:%S')
            fechahora_expedicion = datetime.strptime(fecha_expedicion, '%d-%m-%Y %H:%M:%S')
            print("fecha_hora: ",fechahora_pago)
            print("entrada",entrada)

            equipo = Equipo.objects.filter(id=1)
            folio = Boleto.objects.filter(folio_boleto = folio_boleto, fecha_expedicion_boleto = fechahora_expedicion, entrada = entrada)
            transaccion = Transaccion.objects.create(     no_provedor=no_provedor,
                                                det_estacionamiento=det_estacionamiento,
                                                fecha_pago=fechahora_pago,
                                                expedidor_boleto=entrada,
                                                codigo=codigo,
                                                registrado=registrado,
                                                equipo_id=equipo[0],
                                                folio_boleto=folio[0],
                                                monto=monto,
                                                cambio=cambio,
                                                monedas=monedas,
                                                billetes=billetes,
                                                cambio_entregado=cambio_entregado,
                                                #tienda_id=tienda[0],
                                                )

            if transaccion:
                print("Se encontro:",transaccion)
                #print("Monto: ", boleto[0].monto)
                #monto = boleto[0].monto
                #codigo = boleto[0].codigo
                content = {
                    'registroTransaccion':{
                    'codigo': 1,
                    'codigoError': "00",
                    'descripcionError': "Registro exitoso",
                    }
                }
            else:
                content = {
                'registroTransaccion':{
                'folio': folio_boleto,
                'codigoError': "02",
                'descripcionError': "Boleto NO encontrado",
                }

                }
                print("No se encontro:",transaccion)
        else: #except
            print("Error al extraer datos")
            content = {
                'registroBoleto':{
                'folio': folio_boleto,
                'codigoError': "01",
                'descripcionError': "Inconsistencia de datos",
                }

            }
        return Response(content)

class consultaTransaccionEumApiView(APIView):
    """
    A view that returns the count of active users in JSON.
    """
    #Ejemplo : http://127.0.0.1:8000/api/consultaBoleto/?idboleto=12050821140000557201&te=001&tr=0001&tda=5572
    renderer_classes = [JSONRenderer]
    def post(self, request, format=None):
        #idBoleto = self.request.GET.get('idboleto')
        folio = self.request.data.get('consultaTransaccionEum').get('folio_boleto')
        entrada = self.request.data.get('consultaTransaccionEum').get('entrada')
        fecha_pago = self.request.data.get('consultaTransaccionEum').get('fecha_pago')
        tda = self.request.data.get('consultaTransaccionEum').get('tienda')
        print("folio:  , tienda: ",folio,tda)
        if 1:
            tienda = Tienda.objects.filter(id_tienda=tda,activo=True)
            print("Tienda:",tienda)
            if tienda:
                pass
            else:
                content = {
                'consultaTransaccionEum':{
                'codigo': 4,
                'descripcionError': "Cobro NO habilitado para esta tienda",
                }
                }
                return Response(content)




            fechahora_pago = datetime.strptime(fecha_pago, '%d-%m-%Y %H:%M:%S')


            print("fecha_hora: ",fechahora_pago)
            print("entrada",entrada)

            transaccion = Transaccion.objects.filter(fecha_pago=fechahora_pago,expedidor_boleto=entrada)

            if transaccion:
                print("Se encontro:",transaccion)
                #print("Monto: ", boleto[0].monto)
                proveedor = transaccion[0].no_provedor
                codigo = transaccion[0].codigo
                registrado = transaccion[0].registrado
                monto = transaccion[0].monto
                cambio = transaccion[0].cambio
                monedas = transaccion[0].monedas
                billetes = transaccion[0].billetes
                cambio_entregado = transaccion[0].cambio_entregado
                folio = transaccion[0].folio_boleto.id
                equipo = transaccion[0].equipo_id.id

                boleto = Boleto.objects.filter(id=folio)
                folio_boleto = boleto[0].folio_boleto

                content = {
                    'consultaTransaccionEum':{
                    "no_provedor": proveedor,
                    'fecha_pago': fecha_pago,
                    'expedidor_boleto': entrada,
                     'codigo': codigo,
                     "registrado": registrado,
                    "monto": monto,
                    "cambio": cambio,
                    "monedas": monedas,
                    "billetes": billetes,
                    "cambio_entregado": cambio_entregado,
                    'folio_boleto': folio_boleto,
                    "equipo_id": equipo,
                    'descripcion_codigo': "Pago encontrado",
                    }


                }
            else:
                content = {
                'consultaTransaccionEum':{
                'folio': folio,
                'codigo': 0,
                'descripcionError': "Pago NO encontrado",
                }

                }
                print("No se encontro:",transaccion)
        else: #except
            print("Error al extraer datos")
            content = {
                'consultaTransaccionEum':{
                'folio': folio,
                'codigo': 0,
                'descripcionError': "Inconsistencia de datos",
                }

            }
        return Response(content)


class consultaBoletoEumApiView(APIView):
    """
    A view that returns the count of active users in JSON.
    """
    #Ejemplo : http://127.0.0.1:8000/api/consultaBoleto/?idboleto=12050821140000557201&te=001&tr=0001&tda=5572
    renderer_classes = [JSONRenderer]
    def post(self, request, format=None):
        #idBoleto = self.request.GET.get('idboleto')
        folio = self.request.data.get('consultaBoletoEumRequest').get('folio')
        entrada = self.request.data.get('consultaBoletoEumRequest').get('entrada')
        fecha_expedicion = self.request.data.get('consultaBoletoEumRequest').get('fecha_expedicion')
        tda = self.request.data.get('consultaBoletoEumRequest').get('tienda')
        print("folio:  , tienda: ",folio,tda)
        if 1:
            tienda = Tienda.objects.filter(id_tienda=tda,activo=True)
            print("Tienda:",tienda)
            if tienda:
                pass
            else:
                content = {
                'consultaBoletoEumRequest':{
                'folio': folio,
                'codigo': 4,
                'descripcionError': "Cobro NO habilitado para esta tienda",
                }
                }
                return Response(content)




            fechahora_boleto = datetime.strptime(fecha_expedicion, '%d-%m-%Y %H:%M:%S')


            print("fecha_hora: ",fechahora_boleto)
            print("entrada",entrada)

            boleto = Boleto.objects.filter(fecha_expedicion_boleto=fechahora_boleto,entrada=entrada)

            if boleto:
                print("Se encontro:",boleto)
                #print("Monto: ", boleto[0].monto)
                #monto = boleto[0].monto
                id_boleto = boleto[0].id
                content = {
                    'consultaBoletoEumRequest':{
                    'folio': folio,
                    'id_boleto': id_boleto,
                    'entrada': entrada,
                    'fecha_expedicion': fecha_expedicion,
                    'codigo': 1,
                    'descripcion_codigo': "Boleto encontrado",
                    }
                }
            else:
                content = {
                'consultaBoletoEumRequest':{
                'folio': folio,
                'codigo': 0,
                'descripcionError': "Boleto NO valido",
                }

                }
                print("No se encontro:",boleto)
        else: #except
            print("Error al extraer datos")
            content = {
                'consultaBoletoEumRequest':{
                'folio': folio,
                'codigo': 0,
                'descripcionError': "Inconsistencia de datos",
                }

            }
        return Response(content)

class notiBoletoPagadoApiView(APIView):
    #Ejemplo : http://127.0.0.1:8000/api/consultaBoleto/?idboleto=12020821130000557201&te=001&tr=0001&tda=5572
    renderer_classes = [JSONRenderer]
    def post(self, request, format=None):
        #idBoleto = self.request.GET.get('idboleto')
        idBoleto = self.request.data.get('notiBoletoPagadoRequest').get('idBoleto')
        te = self.request.data.get('notiBoletoPagadoRequest').get('te')
        tr = self.request.data.get('notiBoletoPagadoRequest').get('tr')
        tda = self.request.data.get('notiBoletoPagadoRequest').get('tda')
        #idBoleto2 = self.request.data.get('consultaBoletoRequest').get('idBoleto')
        #print("idboleto222", idBoleto2)
        exitosos = 0
        incidencias = 0
        cancelados = 0
        ingreso = 0
        operaciones = 0
        print("idBoleto:  , tienda: ",idBoleto,tda)
        #print("Proveedor: ",idBoleto[0:2])
        #print("Dia: ",idBoleto[2:4])
        calculador = Calculador()
        try: #try
            print (len(idBoleto))
            if len(idBoleto) == 20:
                proovedor = idBoleto[0:2]
                if int(proovedor) == no_proveedor:
                    pass
                else:
                    content = {
                    "notiBoletoPagado": {
                    "idBoleto": idBoleto,
                    "impresionPantalla": "Gracias por su compra",
                    "impresionTicket": "Compre Walmart",
                    "codRepuesta": "01",
                    "codigoError": "02",
                    "descripcionError": "BOLETO NO VALIDO",
                    "numAutorizacion": ""
                    }
                    }
                    print("Proveedor invalido:",idBoleto)
                    return Response(content)
            else:
                content = {
                "notiBoletoPagado": {
                "idBoleto": idBoleto,
                "impresionPantalla": "Gracias por su compra",
                "impresionTicket": "Compre Walmart",
                "codRepuesta": "01",
                "codigoError": "02",
                "descripcionError": "BOLETO NO VALIDO",
                "numAutorizacion": ""
                }
                }
                print("Longitud de id incorrecta:",idBoleto)
                return Response(content)

            tienda = Tienda.objects.filter(id_tienda=tda,activo=True)
            print("Tienda:",tienda)
            det_estacionamiento = idBoleto[14:18]
            if (tienda and (tda == str(det_estacionamiento))):
                pass
            else:
                content = {
                "notiBoletoPagado": {
                "idBoleto": "",
                "impresionPantalla": "Gracias por su compra",
                "impresionTicket": "Compre Walmart",
                "monto": "",
                "codRepuesta": "01",
                "codigoError": "04",
                "descripcionError": "COBRO NO HABILITADO PARA ESTA TIENDA",
                "numAutorizacion": ""
                }
                }


                return Response(content)


            #Obtener datos
            proovedor = idBoleto[0:2]
            mes_boleto = idBoleto[2:4]
            dia_boleto = idBoleto[4:6]
            anio_boleto = idBoleto[6:8]
            hora_boleto = idBoleto[8:10]
            minuto_boleto = idBoleto[10:12]
            segundo_boleto = idBoleto[12:14]
            det_estacionamiento = idBoleto[14:18]
            entrada = idBoleto[18:20]
            fecha_boleto_amd_walmart =  dia_boleto + "/" + mes_boleto + "/" + anio_boleto
            hora_boleto_walmart = hora_boleto + ":" + minuto_boleto
            fecha_actual = datetime.now().strftime('%d/%m/%y')
            hora_actual = datetime.now().strftime('%H:%M')
            print("Hora y fecha actual:", fecha_actual, hora_actual)


            fecha_boleto = dia_boleto + "-" + mes_boleto + "-" + anio_boleto
            hora_boleto = hora_boleto + ":" + minuto_boleto + ":" + segundo_boleto
            sec = datetime.strptime("01:00:31", '%H:%M:%S')
            fechahora_boleto = datetime.strptime(str(fecha_boleto)+" "+str(hora_boleto), '%d-%m-%y %H:%M:%S')
            #print("fecha_hora: ",fechahora_boleto)
            #print("entrada",entrada)


            boleto = Boleto.objects.filter(fecha_expedicion_boleto=fechahora_boleto,entrada=entrada)
            #transaccion = Transaccion.objects.filter(fecha_expedicion_boleto=fechahora_boleto,expedidor_boleto=entrada)




            if boleto:
                fecha_consulta = datetime.strftime(boleto[0].updated.date(), '%d-%m-%y')
                fecha_consulta_walmart = datetime.strftime(boleto[0].updated.date(), '%d/%m/%y')
                hora_consulta = boleto[0].updated.time()

                print("Fecha_hora_conusltaaaa:", fecha_consulta,hora_consulta)
                print("Folio Boleto:", boleto[0].folio_boleto,boleto[0].id)

                fechahora_consulta = datetime.strptime(str(fecha_consulta)+" "+str(hora_consulta)[:8], '%d-%m-%y %H:%M:%S')
                print("Fecha_hora_conusltaaaa2:", fechahora_consulta)

                fechahora_consulta = datetime.strftime(fechahora_consulta, '%Y-%m-%d %H:%M:%S')
                print("Fecha_hora_boleto:", fechahora_boleto)

                #print("FECHA consulta:", fecha_consulta)

                #print("hora consulta", str(hora_consulta)[:8], str(fecha_consulta))
                #monto = calculador.calcular_tarifa(str(fecha_boleto),str(hora_boleto),0)

                resta = calculador.restar_hora(str(hora_consulta)[:8], str(fecha_consulta))
                #print("resta", resta)
                dias = resta[0]
                segundos = resta[1]
                minutos_transcurridos_consulta = int(segundos/60)
                if dias:
                    minutos_transcurridos_consulta += dias*1440
                #print("minutos totales: {}".format(minutos_transcurridos_consulta))
                print("Minutos transcurridos desde consulta de boleto:", minutos_transcurridos_consulta)
                print("FECHASS:", fecha_consulta,fecha_boleto)
                #resultado = calculador.calcular_tarifa(str(fecha_consulta), str(hora_consulta)[:8], str(fecha_boleto),str(hora_boleto),0)
                fecha_actual_amd = datetime.now().strftime('%d-%m-%y')
                hora_actual_amd = datetime.now().strftime('%H:%M:%S')
                print("Datos calculo:",fecha_actual_amd, hora_actual_amd,fecha_boleto,hora_boleto)
                resultado = calculador.calcular_tarifa(str(fecha_actual_amd), str(hora_actual_amd), str(fecha_boleto),str(hora_boleto),0)
                print("RESULTADO:",resultado)
                """asr = asr
                dias = resultado[0]
                segundos = resultado[1]
                minutos_transcurridos_expedido = int(segundos/60)
                if dias:
                    minutos_transcurridos_expedido += dias*1440
                """
                monto_resultado = resultado[0]
                minutos_transcurridos_expedido = resultado[1]
                print("Tiempo transcurrido desde creacion de boleto:", minutos_transcurridos_expedido)
                minutos_transcurridos_consulta =  minutos_transcurridos_consulta+360 #forza utc
                if minutos_transcurridos_consulta > 14:
                    content = {
                    "notiBoletoPagado": {
                        "idBoleto": idBoleto,
                        "impresionPantalla": "Gracias por su compra",
                        "impresionTicket": "Compre Walmart",
                        "fechaEntrada": fecha_boleto_amd_walmart,
                        "horaEntrada": hora_boleto_walmart,
                        #"fechaCobro": str(fecha_consulta_walmart),
                        #"horaCobro": str(hora_consulta)[:6],
                        "fechaCobro": str(fecha_actual),
                        "horaCobro": str(hora_actual),
                        "duracion": str(minutos_transcurridos_expedido)+" min",
                        "codRepuesta": "00",
                        "codigoError": "05",
                        "descripcionError": "Tiempo agotado Escanea boleto nuevamente",
                        "montoNuevo": float(monto_resultado),
                        "tiempoAdicional": "10 min",
                        "numAutorizacion": ""
                }
                }
                    return Response(content)


                print("Se encontro:",boleto)

                """
                monto = transaccion[0].monto
                codigo = transaccion[0].codigo
                fecha_entrada = transaccion[0].fecha_expedicion_boleto.date().strftime("%d/%m/%y")
                hora_entrada = transaccion[0].fecha_expedicion_boleto.time().strftime("%H:%M")
                print("Monto: ", transaccion[0].monto)
                print("Fecha entrada: ", fecha_entrada, type(fecha_entrada))
                print("Hora entrada: ", hora_entrada)
                """

                print("Fecha_hora_conuslta:", fechahora_consulta)
                equipo = Equipo.objects.filter(id=1)
                #folio = Boleto.objects.filter(folio_boleto=folio_boleto)
                #transaccion = Transaccion.objects.delete(id=4)


                #print("DELETEEEE")
                #transaccion = Transaccion.objects.filter(id=4).delete()

                #asd = asfasad


                try:
                    fechahora_actual = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    transaccion = Transaccion.objects.create(     no_provedor=proovedor,
                                                    det_estacionamiento=det_estacionamiento,
                                                    fecha_pago=fechahora_actual,
                                                    expedidor_boleto=entrada,
                                                    codigo="2",
                                                    registrado=True,
                                                    equipo_id=equipo[0],
                                                    folio_boleto=boleto[0],
                                                    monto=str(monto_resultado),
                                                    cambio=0,
                                                    monedas="0:0",
                                                    billetes="0:0",
                                                    #cambio_entregado="0:0"
                                                    #tienda_id=tienda[0],
                                                    )
                except:
                    #Excepcion para BOLETO PAGADO
                    content = {
                    "notiBoletoPagado": {
                    "idBoleto": idBoleto,
                    "impresionPantalla": "Gracias por su compra",
                    "impresionTicket": "Compre Walmart",
                    "monto": "",
                    "codRepuesta": "01",
                    "codigoError": "02",
                    "descripcionError": "BOLETO PREVIAMENTE PAGADO.",
                    "numAutorizacion": ""
                }
                }
                    return Response(content)

                print("RESULTADO registro transaccion:", transaccion)


                content = {
                    "notiBoletoPagado": {
                        "idBoleto": idBoleto,
                        "impresionPantalla": "Gracias por su compra",
                        "impresionTicket": "Compre Walmart",
                        "fechaEntrada": fecha_boleto_amd_walmart,
                        "horaEntrada": hora_boleto_walmart,
                        #"fechaCobro": str(fecha_consulta_walmart),
                        #"horaCobro": str(hora_consulta)[:6],
                        "fechaCobro": str(fecha_actual),
                        "horaCobro": str(hora_actual),
                        "duracion": str(minutos_transcurridos_expedido)+" min",
                        "codRepuesta": "00",
                        "codigoError": "00",
                        "descripcionError": "",
                        "montoNuevo": "",
                        "tiempoAdicional": "",
                        "numAutorizacion": str(random.randrange(1,999999))
                }
                }

            else:
                content = {
                "notiBoletoPagado": {
                "idBoleto": idBoleto,
                "impresionPantalla": "Gracias por su compra",
                "impresionTicket": "Compre Walmart",
                "monto": "",
                "codRepuesta": "01",
                "codigoError": "02",
                "descripcionError": "BOLETO NO VALIDO",
                "numAutorizacion": ""
                }
                }
                print("No se encontro:",boleto)
        except: #except
            print("Error al extraer datos")
            content = {
                "notiBoletoPagado": {
                "idBoleto": idBoleto,
                "impresionPantalla": "Gracias por su compra",
                "impresionTicket": "Compre Walmart",
                "monto": "",
                "codRepuesta": "01",
                "codigoError": "02",
                "descripcionError": "BOLETO NO VALIDO.",
                "numAutorizacion": ""
                }
                }
        return Response(content)



class revBoletoPagadoApiView(APIView):
    #Ejemplo : http://127.0.0.1:8000/api/consultaBoleto/?idboleto=12020821130000557201&te=001&tr=0001&tda=5572
    renderer_classes = [JSONRenderer]
    def post(self, request, format=None):
        #idBoleto = self.request.GET.get('idboleto')
        idBoleto = self.request.data.get('revBoletoPagadoRequest').get('idBoleto')
        te = self.request.data.get('revBoletoPagadoRequest').get('te')
        tr = self.request.data.get('revBoletoPagadoRequest').get('tr')
        tda = self.request.data.get('revBoletoPagadoRequest').get('tda')
        #idBoleto2 = self.request.data.get('consultaBoletoRequest').get('idBoleto')
        #print("idboleto222", idBoleto2)
        exitosos = 0
        incidencias = 0
        cancelados = 0
        ingreso = 0
        operaciones = 0
        print("idBoleto:  , tienda: ",idBoleto,tda)
        #print("Proveedor: ",idBoleto[0:2])
        #print("Dia: ",idBoleto[2:4])
        calculador = Calculador()
        try: #try
            print (len(idBoleto))
            if len(idBoleto) == 20:
                proovedor = idBoleto[0:2]
                if int(proovedor) == no_proveedor:
                    pass
                else:
                    content = {
                    "revBoletoPagado": {
                    "idBoleto": idBoleto,
                    "impresionPantalla": "Gracias por su compra",
                    "impresionTicket": "Compre Walmart",
                    "codRepuesta": "01",
                    "codigoError": "02",
                    "descripcionError": "BOLETO NO VALIDO",
                    "numAutorizacion": ""
                    }
                    }
                    print("Proveedor invalido:",idBoleto)
                    return Response(content)
            else:
                content = {
                "revBoletoPagado": {
                "idBoleto": idBoleto,
                "impresionPantalla": "Gracias por su compra",
                "impresionTicket": "Compre Walmart",
                "codRepuesta": "01",
                "codigoError": "02",
                "descripcionError": "BOLETO NO VALIDO",
                "numAutorizacion": ""
                }
                }
                print("Longitud de id incorrecta:",idBoleto)
                return Response(content)

            tienda = Tienda.objects.filter(id_tienda=tda,activo=True)
            print("Tienda:",tienda)
            det_estacionamiento = idBoleto[14:18]
            if (tienda and (tda == str(det_estacionamiento))):
                pass
            else:
                content = {
                "revBoletoPagado": {
                "idBoleto": "",
                "impresionPantalla": "Gracias por su compra",
                "impresionTicket": "Compre Walmart",
                "monto": "",
                "codRepuesta": "01",
                "codigoError": "04",
                "descripcionError": "COBRO NO HABILITADO PARA ESTA TIENDA",
                "numAutorizacion": ""
                }
                }


                return Response(content)


            #Obtener datos
            proovedor = idBoleto[0:2]
            mes_boleto = idBoleto[2:4]
            dia_boleto = idBoleto[4:6]
            anio_boleto = idBoleto[6:8]
            hora_boleto = idBoleto[8:10]
            minuto_boleto = idBoleto[10:12]
            segundo_boleto = idBoleto[12:14]
            det_estacionamiento = idBoleto[14:18]
            entrada = idBoleto[18:20]
            fecha_boleto_amd_walmart =  dia_boleto + "/" + mes_boleto + "/" + anio_boleto
            hora_boleto_walmart = hora_boleto + ":" + minuto_boleto
            fecha_actual = datetime.now().strftime('%d/%m/%y')
            hora_actual = datetime.now().strftime('%H:%M')
            print("Hora y fecha actual:", fecha_actual, hora_actual)


            fecha_boleto = dia_boleto + "-" + mes_boleto + "-" + anio_boleto
            hora_boleto = hora_boleto + ":" + minuto_boleto + ":" + segundo_boleto
            sec = datetime.strptime("01:00:31", '%H:%M:%S')
            fechahora_boleto = datetime.strptime(str(fecha_boleto)+" "+str(hora_boleto), '%d-%m-%y %H:%M:%S')
            #print("fecha_hora: ",fechahora_boleto)
            #print("entrada",entrada)


            boleto = Boleto.objects.filter(fecha_expedicion_boleto=fechahora_boleto,entrada=entrada)
            transaccion = Transaccion.objects.filter(folio_boleto=boleto[0]).delete()

            print("Boleto encontrado", boleto[0].id)
            if int(transaccion[0]):

                print("Transaccion eliminada:", transaccion)


                content = {
                "revBoletoPagado": {
                "idBoleto": idBoleto,
                "impresionPantalla": "Gracias por su compra",
                "impresionTicket": "Compre Walmart",
                "codRepuesta": "00",
                "codigoError": "01",
                "descripcionError": "REVERSO EXITOSO",
                "numAutorizacion": str(random.randrange(1,999999))
                }
                }

            else:
                content = {
                "revBoletoPagado": {
                "idBoleto": idBoleto,
                "impresionPantalla": "Gracias por su compra",
                "impresionTicket": "Compre Walmart",
                "codRepuesta": "01",
                "codigoError": "01",
                "descripcionError": "REVERSO INCORRECTO",
                "numAutorizacion": ""
                }
                }
                print("No se encontro:",boleto)
        except: #except
            print("Error al extraer datos")
            content = {
                "revBoletoPagado": {
                "idBoleto": idBoleto,
                "impresionPantalla": "Gracias por su compra",
                "impresionTicket": "Compre Walmart",
                "codRepuesta": "01",
                "codigoError": "02",
                "descripcionError": "BOLETO NO VALIDO.",
                "numAutorizacion": ""
                }
                }
        return Response(content)



#@method_decorator(staff_member_required, name="dispatch")


class consultarTransaccion(APIView):
    def post(self, request):

        contenido = {}

        datos = self.request.data.get('consultarTransaccion')

        folio    = datos.get('folio')
        entrada  = datos.get('entrada')
        fecha    = datos.get('fecha')
        tienda   = datos.get('tienda')

        print ('{}:  folio {}, entrada {}, fecha {}, tienda {}'
            .format(self, folio, entrada, fecha, tienda))

        # obtener id de la tienda
        tienda = Tienda.objects.filter(id_tienda=tienda, activo=True)
        print ('{}: tienda {}'.format(self, tienda))

        if tienda:
            idTienda  = tienda[0].id
            print ('{}: tienda_id {}'.format(self, idTienda))

            # obtenerBoleto

            boleto = Boleto.objects.filter(folio_boleto = folio,
                                            entrada = entrada,
                                            fecha_expedicion_boleto = fecha,
                                            tienda_id = idTienda
                                                )

            if boleto:
                # TODO: El corregir el modelo boleto ya que estos pueden no ser únicos
                print ('{}: Boleto {}'.format(self, boleto))
                idBoleto = boleto[0].id
                print ('{}: Boleto {}'.format(self, idBoleto))

                # obtener transacciones
                transacciones = Transaccion.objects.filter(folio_boleto = idBoleto)
                print ('{}: Transacciones : {}'.format(self, transacciones))

                if transacciones:
                    # TODO: Corregir modelo transacciones ya que unicamente admite una transacción
                    print ('{}: Transacciones encontradas: {}'.format(self, transacciones))
                    serializer = TransaccionSerializer(transacciones, many=True)
                    return Response({'transacciones' : serializer.data})
                else:
                    contenido = {
                        'mensaje': 'No se encontraron transacciones'
                    }

            else:
                contenido = {
                    'mensaje': 'No se encontro el boleto'
                }

        else:
            contenido = {
                'mensaje': 'No se encontro la tienda'
            }
        return Response({
                'consultarTransaccion': contenido
            } )

    def __str__(self):
        return "{} ".format( 'Transacciones'.ljust( 15 ) )