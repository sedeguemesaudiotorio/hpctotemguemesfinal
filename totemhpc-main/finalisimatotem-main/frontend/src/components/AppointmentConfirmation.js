import React from 'react';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Separator } from './ui/separator';
import { ArrowLeft, User, Calendar, Clock, MapPin, CheckCircle } from 'lucide-react';
import Header from './Header';

const AppointmentConfirmation = ({ patient, onBack, onConfirm, isLoading }) => {
  if (!patient) {
    return (
      <div className="min-h-screen flex items-center justify-center p-8" style={{
        background: '#4A90E2'
      }}>
        <Card className="w-full max-w-lg shadow-2xl border-0 bg-white">
          {/* Header del hospital */}
          <Header />
          
          <CardContent className="p-8 text-center" style={{
            background: '#4A90E2'
          }}>
            <div className="w-16 h-16 bg-red-500 rounded-full flex items-center justify-center mx-auto mb-4">
              <User className="w-8 h-8 text-white" />
            </div>
            <h2 className="text-2xl font-bold text-white mb-4">
              Paciente no encontrado
            </h2>
            <p className="text-blue-100 mb-6">
              No se encontró un turno asignado para el documento ingresado.
            </p>
            <Button
              onClick={onBack}
              className="w-full h-12 text-lg font-medium bg-gray-700 hover:bg-gray-800 text-white"
            >
              <ArrowLeft className="w-5 h-5 mr-2" />
              Volver
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-8" style={{
      background: '#4A90E2'
    }}>
      <Card className="w-full max-w-2xl shadow-2xl border-0 bg-white">
        {/* Header del hospital */}
        <Header />
        
        <CardContent className="p-8" style={{
          background: '#4A90E2'
        }}>
          <div className="text-center mb-8">
            <div className="w-16 h-16 bg-green-600 rounded-full flex items-center justify-center mx-auto mb-4">
              <User className="w-8 h-8 text-white" />
            </div>
            <h1 className="text-2xl font-bold text-white mb-4">
              Confirmación de Turno
            </h1>
          </div>
          
          <div className="space-y-6">
            <div className="bg-white bg-opacity-90 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
                <User className="w-5 h-5 mr-2" />
                Datos del Paciente
              </h3>
              <div className="text-2xl font-bold text-gray-900">
                {patient.nombre} {patient.apellido}
              </div>
            </div>
            
            <div className="bg-white bg-opacity-90 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
                <Calendar className="w-5 h-5 mr-2" />
                Información del Turno
              </h3>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-gray-600">Médico:</span>
                  <span className="font-semibold text-gray-900">{patient.turno.medico}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-600">Hora:</span>
                  <Badge variant="outline" className="text-lg font-mono">
                    <Clock className="w-4 h-4 mr-1" />
                    {patient.turno.hora}
                  </Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-600">Piso:</span>
                  <Badge className="text-lg bg-blue-600">
                    <MapPin className="w-4 h-4 mr-1" />
                    {patient.turno.piso}
                  </Badge>
                </div>
              </div>
            </div>
            
            <div className="space-y-4">
              <Button
                onClick={onConfirm}
                disabled={isLoading}
                className="w-full h-14 text-lg font-semibold bg-green-600 hover:bg-green-700 transition-all duration-300 transform hover:scale-105"
              >
                <CheckCircle className="w-6 h-6 mr-2" />
                {isLoading ? 'Confirmando...' : 'Confirmar'}
              </Button>
              
              <Button
                onClick={onBack}
                className="w-full h-12 text-lg font-medium bg-gray-700 hover:bg-gray-800 text-white"
              >
                <ArrowLeft className="w-5 h-5 mr-2" />
                Volver
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default AppointmentConfirmation;