import React, { useState, useEffect } from 'react';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { ArrowLeft, User, AlertCircle, Delete, Check } from 'lucide-react';
import { Alert, AlertDescription } from './ui/alert';

const DocumentInput = ({ onBack, onSubmit, title, isLoading }) => {
  const [document, setDocument] = useState('');
  const [error, setError] = useState('');

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

  const handleSubmit = () => {
    if (!document.trim()) {
      setError('Por favor ingrese su número de documento');
      return;
    }
    if (document.length < 7) {
      setError('El número de documento debe tener al menos 7 dígitos');
      return;
    }
    setError('');
    onSubmit(document);
  };

  const handleNumberClick = (number) => {
    if (document.length < 10) {
      setDocument(document + number);
      if (error) setError('');
    }
  };

  const handleDelete = () => {
    setDocument(document.slice(0, -1));
    if (error) setError('');
  };

  const handleClear = () => {
    setDocument('');
    if (error) setError('');
  };

  // Números del teclado en el orden mostrado en la imagen
  const keypadNumbers = [
    ['1', '2', '3'],
    ['4', '5', '6'],
    ['7', '8', '9'],
    ['', '0', '']
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-400 via-blue-500 to-blue-600 flex items-center justify-center p-8">
      <Card className="w-full max-w-2xl shadow-2xl border-0 bg-white">
        {/* Header del hospital */}
        <div className="bg-white px-6 py-4 rounded-t-lg">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <img 
                src="/new_hpc_logo.jpg" 
                alt="HPC Logo" 
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
            <div className="text-xl font-bold text-gray-700">
              Terminal de Autogestión
            </div>
          </div>
        </div>

        <CardContent className="bg-gradient-to-br from-blue-400 via-blue-500 to-blue-600 p-8 rounded-b-lg">
          {/* Título */}
          <div className="text-center mb-8">
            <h1 className="text-white text-2xl font-semibold">
              Ingrese su número de documento
            </h1>
            <p className="text-white text-lg mt-2">
              luego presione aceptar
            </p>
          </div>

          {/* Display del número ingresado */}
          <div className="mb-8">
            <div className="bg-gray-100 border-2 border-gray-300 rounded-lg p-4 text-center">
              <div className="text-3xl font-mono text-gray-800 min-h-[40px] flex items-center justify-center">
                {document || ''}
              </div>
            </div>
          </div>

          {error && (
            <Alert variant="destructive" className="mb-6">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          {/* Teclado numérico */}
          <div className="grid grid-cols-3 gap-4 max-w-md mx-auto mb-8">
            {keypadNumbers.map((row, rowIndex) => 
              row.map((num, colIndex) => {
                if (num === '') {
                  // Botones especiales en la fila inferior
                  if (rowIndex === 3) {
                    if (colIndex === 0) {
                      return (
                        <Button
                          key={`delete-${rowIndex}-${colIndex}`}
                          onClick={handleDelete}
                          className="h-16 w-full text-lg font-bold bg-orange-400 hover:bg-orange-500 text-white border-2 border-orange-500"
                          disabled={isLoading || !document}
                        >
                          BORRAR
                        </Button>
                      );
                    } else if (colIndex === 2) {
                      return (
                        <Button
                          key={`accept-${rowIndex}-${colIndex}`}
                          onClick={handleSubmit}
                          className="h-16 w-full text-lg font-bold bg-green-500 hover:bg-green-600 text-white border-2 border-green-600"
                          disabled={isLoading || !document}
                        >
                          ACEPTAR
                        </Button>
                      );
                    }
                  }
                  return <div key={`empty-${rowIndex}-${colIndex}`} className="h-16"></div>;
                }
                
                return (
                  <Button
                    key={num}
                    onClick={() => handleNumberClick(num)}
                    className="h-16 w-full text-2xl font-bold bg-gray-200 hover:bg-gray-300 text-gray-800 border-2 border-gray-400 transition-all duration-150 active:bg-gray-400"
                    disabled={isLoading}
                  >
                    {num}
                  </Button>
                );
              })
            )}
          </div>

          {/* Botón volver */}
          <div className="text-center">
            <Button
              onClick={onBack}
              variant="outline"
              className="bg-gray-600 hover:bg-gray-700 text-white border-gray-600 px-8 py-3"
            >
              <ArrowLeft className="w-5 h-5 mr-2" />
              Volver
            </Button>
          </div>

          {isLoading && (
            <div className="text-center mt-4">
              <div className="text-white text-lg">Buscando...</div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default DocumentInput;