import React, { useEffect } from 'react';
import { Button } from './ui/button';
import { Card, CardContent } from './ui/card';

const WelcomeScreen = ({ onOptionSelect }) => {
  // Auto-restart functionality after 30 seconds of inactivity
  useEffect(() => {
    const timer = setTimeout(() => {
      // This will reload the page, effectively restarting the screen
      window.location.reload();
    }, 30000);

    // Clear timeout on component unmount or user interaction
    const handleUserActivity = () => {
      clearTimeout(timer);
    };

    // Add event listeners for user activity
    window.addEventListener('click', handleUserActivity);
    window.addEventListener('keydown', handleUserActivity);
    window.addEventListener('touchstart', handleUserActivity);

    return () => {
      clearTimeout(timer);
      window.removeEventListener('click', handleUserActivity);
      window.removeEventListener('keydown', handleUserActivity);
      window.removeEventListener('touchstart', handleUserActivity);
    };
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-400 via-blue-500 to-blue-600 flex items-center justify-center p-8">
      <Card className="w-full max-w-2xl shadow-2xl border-0 bg-white">
        {/* Header del hospital */}
        <div className="bg-white px-6 py-4 rounded-t-lg">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <img 
                src="/hospital_logo.png" 
                alt="Hospital Privado de Comunidad Logo" 
                className="h-12 w-auto" 
                onError={(e) => {
                  // Fallback to text if image fails to load
                  e.target.style.display = 'none';
                  e.target.nextSibling.style.display = 'block';
                }}
              />
              <div className="bg-gray-800 text-white px-3 py-2 text-sm font-bold" style={{display: 'none'}}>
                HPC
              </div>
              <div className="text-gray-700 text-sm">
                <div className="font-bold">HOSPITAL PRIVADO</div>
                <div>DE COMUNIDAD</div>
              </div>
            </div>
            {/* Title "Terminal de Autogestión" positioned to not obscure the logo */}
            <div className="text-xl font-bold text-gray-700">
              Terminal de Autogestión
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
              className="w-full h-20 text-xl font-semibold bg-green-600 hover:bg-green-700 text-white border-2 border-green-700 transition-all duration-300 transform hover:scale-105 flex items-center justify-center"
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