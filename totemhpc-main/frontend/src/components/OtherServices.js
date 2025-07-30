import React, { useEffect } from 'react';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Card, CardContent } from './ui/card';
import { ArrowLeft, User } from 'lucide-react';
import { secretaryOptions } from '../services/api';
import Header from './Header';

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

  // Define badge colors for each floor
  const getBadgeColor = (optionId) => {
    const colors = {
      'pb': 'bg-orange-500',
      'pp': 'bg-orange-600', 
      '2p': 'bg-orange-600',
      '3p': 'bg-orange-600'
    };
    return colors[optionId] || 'bg-orange-500';
  };

  const getBadgeText = (optionId) => {
    const texts = {
      'pb': 'Planta Baja',
      'pp': 'Primer Piso',
      '2p': 'Segundo Piso',
      '3p': 'Tercer Piso'
    };
    return texts[optionId] || 'Piso';
  };

  return (
    <div 
      className="min-h-screen flex items-center justify-center p-4" 
      style={{
        background: 'linear-gradient(135deg, #4A90E2 0%, #357ABD 100%)'
      }}
    >
      <Card className="w-full max-w-lg shadow-2xl border-0 bg-white">
        {/* Header del hospital */}
        <Header />
        
        <CardContent className="p-8" style={{
          background: '#4A90E2'
        }}>
          {/* Header Section */}
          <div className="text-center mb-8">
            <div className="w-20 h-20 bg-white bg-opacity-20 rounded-full flex items-center justify-center mx-auto mb-6">
              <User className="w-12 h-12 text-white" />
            </div>
            <h1 className="text-3xl font-bold text-white mb-3">
              Otras Gestiones
            </h1>
            <p className="text-blue-100 text-lg">
              Seleccione la secretaría correspondiente
            </p>
          </div>
          
          {/* Buttons Section */}
          <div className="space-y-4 mb-8">
            {secretaryOptions.map((option) => (
              <Button
                key={option.id}
                onClick={() => onServiceSelect(option)}
                disabled={isLoading}
                className="w-full h-20 bg-blue-600 hover:bg-blue-700 active:bg-blue-800 text-white border-0 rounded-xl shadow-lg transition-all duration-200 hover:shadow-xl hover:scale-[1.02] active:scale-[0.98]"
              >
                <div className="flex items-center justify-between w-full px-2">
                  <span className="text-lg font-semibold text-left">
                    {option.name}
                  </span>
                  <Badge 
                    className={`${getBadgeColor(option.id)} text-white font-medium px-3 py-1 rounded-full text-sm border-0`}
                  >
                    {getBadgeText(option.id)}
                  </Badge>
                </div>
              </Button>
            ))}
          </div>
          
          {/* Back Button */}
          <div className="text-center">
            <Button
              onClick={onBack}
              disabled={isLoading}
              className="bg-gray-700 hover:bg-gray-800 active:bg-gray-900 text-white border-0 px-8 py-3 rounded-xl shadow-lg transition-all duration-200 hover:shadow-xl"
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