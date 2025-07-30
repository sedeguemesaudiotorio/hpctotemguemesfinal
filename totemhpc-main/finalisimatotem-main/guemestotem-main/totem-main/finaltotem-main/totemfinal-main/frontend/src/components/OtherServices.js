import React, { useEffect } from 'react';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { ArrowLeft, Settings, MapPin } from 'lucide-react';
import { secretaryOptions } from '../services/api';

const OtherServices = ({ onBack, onServiceSelect, isLoading }) => {
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
      <Card className="w-full max-w-2xl shadow-2xl border-0">
        <CardHeader className="text-center pb-6">
          <div className="w-16 h-16 bg-blue-600 rounded-full flex items-center justify-center mx-auto mb-4">
            <img 
              src="/floor_selection_icon.png" 
              alt="Secretaria" 
              className="w-12 h-12 object-contain" 
              onError={(e) => {
                // Fallback to settings icon if image fails to load
                e.target.style.display = 'none';
                e.target.nextSibling.style.display = 'block';
              }}
            />
            <Settings className="w-8 h-8 text-white" style={{display: 'none'}} />
          </div>
          <CardTitle className="text-2xl font-bold text-gray-800">
            Otras Gestiones
          </CardTitle>
          <p className="text-gray-600 mt-2">
            Seleccione la secretaría que desea visitar
          </p>
        </CardHeader>
        
        <CardContent className="space-y-6">
          <div className="grid grid-cols-1 gap-4">
            {secretaryOptions.map((option) => (
              <Button
                key={option.id}
                onClick={() => onServiceSelect(option)}
                disabled={isLoading}
                className="w-full h-20 text-lg font-semibold bg-blue-600 hover:bg-blue-700 text-white border-2 border-blue-700 transition-all duration-300 transform hover:scale-105 rounded-lg shadow-lg"
                variant="outline"
              >
                <div className="flex items-center justify-between w-full">
                  <span className="text-xl font-bold">{option.name}</span>
                  <Badge variant="secondary" className="ml-2 bg-yellow-400 text-black font-semibold">
                    <MapPin className="w-4 h-4 mr-1" />
                    {option.floor}
                  </Badge>
                </div>
              </Button>
            ))}
          </div>
          
          <div className="text-center">
            <Button
              onClick={onBack}
              disabled={isLoading}
              variant="outline"
              className="bg-gray-600 hover:bg-gray-700 text-white border-gray-600 px-8 py-3"
            >
              <ArrowLeft className="w-5 h-5 mr-2" />
              Volver
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default OtherServices;