import React, { useEffect } from 'react';
import { Button } from './ui/button';
import { Card, CardContent } from './ui/card';
import { CheckCircle, Clock, Home } from 'lucide-react';
import Header from './Header';

const WaitingMessage = ({ floor, onHome }) => {

  return (
    <div className="min-h-screen flex items-center justify-center p-8" style={{
      background: '#4A90E2'
    }}>
      <Card className="w-full max-w-2xl shadow-2xl border-0 bg-white">
        {/* Header del hospital */}
        <Header />
        
        <CardContent className="p-12 text-center" style={{
          background: '#4A90E2'
        }}>
          <div className="w-24 h-24 bg-green-600 rounded-full flex items-center justify-center mx-auto mb-8 animate-pulse">
            <CheckCircle className="w-12 h-12 text-white" />
          </div>
          
          <div className="space-y-6">
            <h1 className="text-3xl font-bold text-white">
              ¡Proceso Completado!
            </h1>
            
            <div className="bg-white bg-opacity-90 rounded-lg p-6 shadow-inner">
              <div className="flex items-center justify-center mb-4">
                <Clock className="w-8 h-8 text-blue-600 mr-2" />
                <h2 className="text-2xl font-bold text-gray-800">
                  Aguarde en {floor}
                </h2>
              </div>
              
              <div className="space-y-3">
                <p className="text-xl text-gray-700">
                  Por favor tome asiento y aguarde a ser llamado por secretaria.
                </p>
              </div>
            </div>
            
            <div className="text-white font-bold">
              <p className="mb-2">Muchas gracias por su paciencia</p>
              <p className="text-sm">En breve será atendido</p>
            </div>
          </div>
          
          <div className="mt-8 pt-6 border-t border-white border-opacity-30">
            <Button
              onClick={onHome}
              className="h-12 text-lg font-medium px-8 bg-gray-700 hover:bg-gray-800 text-white"
            >
              <Home className="w-5 h-5 mr-2" />
              Volver al inicio
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default WaitingMessage;