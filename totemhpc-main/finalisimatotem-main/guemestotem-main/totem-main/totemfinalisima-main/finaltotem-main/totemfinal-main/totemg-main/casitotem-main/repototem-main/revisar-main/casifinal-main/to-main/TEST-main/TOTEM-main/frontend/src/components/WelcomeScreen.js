import React from 'react';
import { Button } from './ui/button';
import { Card, CardContent } from './ui/card';
import { Calendar, Settings } from 'lucide-react';

const WelcomeScreen = ({ onOptionSelect }) => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-400 via-blue-500 to-blue-600 flex items-center justify-center p-8">
      <Card className="w-full max-w-2xl shadow-2xl border-0 bg-white">
        {/* Header del hospital */}
        <div className="bg-white px-6 py-4 rounded-t-lg">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="bg-gray-800 text-white px-3 py-2 text-sm font-bold">
                HPC
              </div>
              <div className="text-gray-700 text-sm">
                <div className="font-bold">HOSPITAL PRIVADO</div>
                <div>DE COMUNIDAD</div>
              </div>
            </div>
            <div className="text-xl font-bold text-gray-700">
              Terminal de Autogestión
            </div>
            <div className="flex space-x-2">
              <Button variant="outline" size="sm" className="bg-orange-400 text-white border-orange-400">
                ←
              </Button>
              <Button variant="outline" size="sm" className="bg-orange-400 text-white border-orange-400">
                ×
              </Button>
            </div>
          </div>
        </div>

        <CardContent className="bg-gradient-to-br from-blue-400 via-blue-500 to-blue-600 p-12 rounded-b-lg">
          <div className="text-center mb-12">
            <h1 className="text-4xl font-bold text-white mb-4">
              ¿Qué trámite desea realizar?
            </h1>
          </div>
          
          <div className="space-y-6 max-w-lg mx-auto">
            <Button
              onClick={() => onOptionSelect('appointment')}
              className="w-full h-20 text-xl font-semibold bg-yellow-500 hover:bg-yellow-600 text-black border-2 border-yellow-600 transition-all duration-300 transform hover:scale-105"
            >
              Ya Tengo Turno
            </Button>
            
            <Button
              onClick={() => onOptionSelect('other-services')}
              className="w-full h-20 text-xl font-semibold bg-green-600 hover:bg-green-700 text-white border-2 border-green-700 transition-all duration-300 transform hover:scale-105"
            >
              Otras Gestiones
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default WelcomeScreen;