import React, { useState, useEffect } from 'react';
import './App.css';
import WelcomeScreen from './components/WelcomeScreen';
import DocumentInput from './components/DocumentInput';
import AppointmentConfirmation from './components/AppointmentConfirmation';
import OtherServices from './components/OtherServices';
import WaitingMessage from './components/WaitingMessage';
import { patientAPI, serviceAPI, healthAPI } from './services/api';
import { Toaster } from './components/ui/toaster';
import { useToast } from './hooks/use-toast';

function App() {
  const [currentScreen, setCurrentScreen] = useState('welcome');
  const [selectedOption, setSelectedOption] = useState(null);
  const [patientData, setPatientData] = useState(null);
  const [selectedFloor, setSelectedFloor] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [apiStatus, setApiStatus] = useState('unknown');
  const { toast } = useToast();

  // Check API health on mount
  useEffect(() => {
    const checkAPIHealth = async () => {
      const result = await healthAPI.checkHealth();
      setApiStatus(result.success ? 'healthy' : 'unhealthy');
      
      if (!result.success) {
        toast({
          title: "Advertencia",
          description: "API no disponible. Usando modo de prueba.",
          variant: "destructive",
        });
      }
    };

    checkAPIHealth();
  }, [toast]);

  // Auto-restart functionality for completed transactions after 30 seconds
  useEffect(() => {
    if (currentScreen === 'waiting-message') {
      const timer = setTimeout(() => {
        window.location.reload();
      }, 30000);

      return () => clearTimeout(timer);
    }
  }, [currentScreen]);

  const handleOptionSelect = (option) => {
    setSelectedOption(option);
    setCurrentScreen('document-input');
  };

  const handleDocumentSubmit = async (documentNumber) => {
    setIsLoading(true);
    
    try {
      if (selectedOption === 'appointment') {
        // Buscar paciente para confirmar turno
        const result = await patientAPI.findByDocument(documentNumber);
        
        if (result.success) {
          setPatientData(result.data);
          setCurrentScreen('appointment-confirmation');
        } else {
          // Show the specific message for patients without appointments or not registered
          if (result.error === 'no_patient_record' || result.error === 'no_appointment') {
            toast({
              title: "Información",
              description: "Paciente no cuenta con turno programado. Por favor elegir y dirigirse a la secretaria correspondiente.",
              variant: "default",
              duration: 8000,
            });
            // Redirect to other services after showing the message
            setPatientData({ documento: documentNumber });
            setCurrentScreen('other-services');
          } else {
            // For other errors, still redirect to other services
            setPatientData({ documento: documentNumber });
            setCurrentScreen('other-services');
            toast({
              title: "Información",
              description: "Paciente no cuenta con turno programado. Por favor elegir y dirigirse a la secretaria correspondiente.",
              variant: "default",
              duration: 8000,
            });
          }
        }
      } else {
        // Para otras gestiones, solo necesitamos el documento
        setPatientData({ documento: documentNumber });
        setCurrentScreen('other-services');
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Error al procesar la solicitud. Intente nuevamente.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleAppointmentConfirm = async () => {
    if (!patientData) return;
    
    setIsLoading(true);
    
    try {
      const result = await patientAPI.confirmAppointment(patientData.documento);
      
      if (result.success) {
        setSelectedFloor(patientData.turno.piso);
        setCurrentScreen('waiting-message');
        toast({
          title: "Turno confirmado",
          description: "Su turno ha sido confirmado exitosamente.",
        });
      } else {
        toast({
          title: "Error",
          description: "No se pudo confirmar el turno. Intente nuevamente.",
          variant: "destructive",
        });
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Error al confirmar el turno. Intente nuevamente.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleServiceSelect = async (service) => {
    if (!patientData) return;
    
    setIsLoading(true);
    
    try {
      const result = await serviceAPI.logServiceRequest(
        patientData.documento,
        service.id,
        service.floor
      );
      
      if (result.success) {
        setSelectedFloor(service.floor);
        setCurrentScreen('waiting-message');
        toast({
          title: "Solicitud registrada",
          description: `Su solicitud para ${service.name} ha sido registrada.`,
        });
      } else {
        toast({
          title: "Error",
          description: "No se pudo registrar la solicitud. Intente nuevamente.",
          variant: "destructive",
        });
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Error al registrar la solicitud. Intente nuevamente.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleGoHome = () => {
    setCurrentScreen('welcome');
    setSelectedOption(null);
    setPatientData(null);
    setSelectedFloor('');
  };

  const handleBack = () => {
    switch (currentScreen) {
      case 'document-input':
        setCurrentScreen('welcome');
        setSelectedOption(null);
        break;
      case 'appointment-confirmation':
        setCurrentScreen('document-input');
        setPatientData(null);
        break;
      case 'other-services':
        setCurrentScreen('document-input');
        setPatientData(null);
        break;
      default:
        setCurrentScreen('welcome');
    }
  };

  const getDocumentInputTitle = () => {
    return selectedOption === 'appointment' 
      ? 'Confirmación de Turno' 
      : 'Otras Gestiones';
  };

  return (
    <div className="App">
      {/* API Status Indicator */}
      {apiStatus === 'unhealthy' && (
        <div className="fixed top-4 right-4 bg-yellow-500 text-white px-4 py-2 rounded-lg text-sm z-50">
          Modo de prueba - API desconectada
        </div>
      )}
      
      {currentScreen === 'welcome' && (
        <WelcomeScreen onOptionSelect={handleOptionSelect} />
      )}
      
      {currentScreen === 'document-input' && (
        <DocumentInput
          onBack={handleBack}
          onSubmit={handleDocumentSubmit}
          title={getDocumentInputTitle()}
          isLoading={isLoading}
        />
      )}
      
      {currentScreen === 'appointment-confirmation' && (
        <AppointmentConfirmation
          patient={patientData}
          onBack={handleBack}
          onConfirm={handleAppointmentConfirm}
          isLoading={isLoading}
        />
      )}
      
      {currentScreen === 'other-services' && (
        <OtherServices
          onBack={handleBack}
          onServiceSelect={handleServiceSelect}
          isLoading={isLoading}
        />
      )}
      
      {currentScreen === 'waiting-message' && (
        <WaitingMessage
          floor={selectedFloor}
          onHome={handleGoHome}
        />
      )}
      
      <Toaster />
    </div>
  );
}

export default App;