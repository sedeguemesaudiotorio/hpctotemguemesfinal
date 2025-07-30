import React, { useEffect, useState } from 'react';
import { Button } from './ui/button';
import { Card, CardContent } from './ui/card';
import { CheckCircle, Clock, Home } from 'lucide-react';

const WaitingMessage = ({ floor, onHome }) => {
  const [dots, setDots] = useState('');

  useEffect(() => {
    const interval = setInterval(() => {
      setDots(prev => {
        if (prev === '...') return '';
        return prev + '.';
      });
    }, 500);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-green-100 flex items-center justify-center p-8">
      <Card className="w-full max-w-2xl shadow-2xl border-0">
        <CardContent className="p-12 text-center">
          <div className="w-24 h-24 bg-green-600 rounded-full flex items-center justify-center mx-auto mb-8 animate-pulse">
            <CheckCircle className="w-12 h-12 text-white" />
          </div>
          
          <div className="space-y-6">
            <h1 className="text-3xl font-bold text-gray-800">
              ¡Proceso Completado!
            </h1>
            
            <div className="bg-white rounded-lg p-6 shadow-inner">
              <div className="flex items-center justify-center mb-4">
                <Clock className="w-8 h-8 text-blue-600 mr-2" />
                <h2 className="text-2xl font-bold text-gray-800">
                  Aguarde en {floor}
                </h2>
              </div>
              
              <div className="space-y-3">
                <p className="text-xl text-gray-700">
                  Por favor tome asiento y espere el llamado de la secretaria
                </p>
                
                <div className="text-blue-600 font-mono text-lg">
                  Procesando{dots}
                </div>
              </div>
            </div>
            
            <div className="text-gray-600">
              <p className="mb-2">Muchas gracias por su paciencia</p>
              <p className="text-sm">En breve será atendido</p>
            </div>
          </div>
          
          <div className="mt-8 pt-6 border-t border-gray-200">
            <Button
              onClick={onHome}
              variant="outline"
              className="h-12 text-lg font-medium px-8"
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