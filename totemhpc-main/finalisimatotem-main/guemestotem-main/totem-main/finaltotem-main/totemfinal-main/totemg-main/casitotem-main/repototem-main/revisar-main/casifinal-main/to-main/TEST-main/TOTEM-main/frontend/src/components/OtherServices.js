import React from 'react';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { ArrowLeft, Settings, MapPin } from 'lucide-react';
import { secretaryOptions } from '../services/api';

const OtherServices = ({ onBack, onServiceSelect, isLoading }) => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-blue-100 flex items-center justify-center p-8">
      <Card className="w-full max-w-2xl shadow-2xl border-0">
        <CardHeader className="text-center pb-6">
          <div className="w-16 h-16 bg-blue-600 rounded-full flex items-center justify-center mx-auto mb-4">
            <Settings className="w-8 h-8 text-white" />
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
                className="w-full h-16 text-lg font-semibold bg-white hover:bg-gray-50 text-gray-800 border-2 border-gray-200 hover:border-blue-300 transition-all duration-300 transform hover:scale-105"
                variant="outline"
              >
                <div className="flex items-center justify-between w-full">
                  <span>{option.name}</span>
                  <Badge variant="secondary" className="ml-2">
                    <MapPin className="w-4 h-4 mr-1" />
                    {option.floor}
                  </Badge>
                </div>
              </Button>
            ))}
          </div>
          
          <Button
            onClick={onBack}
            disabled={isLoading}
            variant="outline"
            className="w-full h-12 text-lg font-medium"
          >
            <ArrowLeft className="w-5 h-5 mr-2" />
            Volver
          </Button>
        </CardContent>
      </Card>
    </div>
  );
};

export default OtherServices;