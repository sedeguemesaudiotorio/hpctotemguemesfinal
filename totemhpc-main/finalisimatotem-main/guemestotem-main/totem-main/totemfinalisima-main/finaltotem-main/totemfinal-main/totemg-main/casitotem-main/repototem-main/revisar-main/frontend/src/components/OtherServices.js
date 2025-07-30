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
          {/* Secretary icon with black borders as requested */}
          <div className="w-16 h-16 bg-blue-300 rounded-full flex items-center justify-center mx-auto mb-4 border-4 border-black">
            <img 
              src="/secretary_icon.png" 
              alt="Secretaria" 
              className="w-10 h-10 border-2 border-black rounded" 
              onError={(e) => {
                // Fallback to settings icon if image fails to load
                e.target.style.display = 'none';
                e.target.nextSibling.style.display = 'block';
              }}
            />
            <Settings className="w-8 h-8 text-white border-2 border-black rounded" style={{display: 'none'}} />
          </div>
          <CardTitle className="text-2xl font-bold text-gray-800">
            Otras Gestiones
          </CardTitle>
          <p className="text-gray-600 mt-2">
            Seleccione la secretaría correspondiente
          </p>
        </CardHeader>

        <CardContent className="space-y-4">
          {secretaryOptions.map((option) => (
            <Button
              key={option.id}
              onClick={() => onServiceSelect(option)}
              disabled={isLoading}
              className="w-full h-16 text-lg font-semibold bg-white hover:bg-gray-50 text-gray-800 border-2 border-gray-300 hover:border-blue-500 transition-all duration-300 transform hover:scale-105 flex items-center justify-between px-6"
            >
              <div className="flex items-center space-x-3">
                <MapPin className="w-6 h-6 text-blue-600" />
                <span>{option.name}</span>
              </div>
              <Badge variant="secondary" className="bg-blue-100 text-blue-800">
                {option.floor}
              </Badge>
            </Button>
          ))}

          <div className="pt-6">
            <Button
              onClick={onBack}
              disabled={isLoading}
              variant="outline"
              className="w-full h-12 text-lg font-semibold border-2 border-gray-300 hover:border-gray-400 transition-all duration-300"
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