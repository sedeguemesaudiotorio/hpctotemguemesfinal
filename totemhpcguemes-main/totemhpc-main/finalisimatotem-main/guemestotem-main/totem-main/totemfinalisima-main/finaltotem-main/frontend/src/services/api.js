import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Create axios instance with default config
const apiClient = axios.create({
  baseURL: API,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor for logging
apiClient.interceptors.request.use(
  (config) => {
    console.log(`🔵 API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('❌ API Request Error:', error);
    return Promise.reject(error);
  }
);

// Add response interceptor for logging and error handling
apiClient.interceptors.response.use(
  (response) => {
    console.log(`✅ API Response: ${response.status} ${response.config.url}`);
    return response;
  },
  (error) => {
    console.error('❌ API Response Error:', error.response?.status, error.response?.data);
    return Promise.reject(error);
  }
);

export const patientAPI = {
  // Buscar paciente por documento
  findByDocument: async (documento) => {
    try {
      const response = await apiClient.get(`/patients/${documento}`);
      
      if (response.data.status === 'success') {
        return { success: true, data: response.data.data };
      }
      
      return { success: false, error: 'Error inesperado en respuesta' };
    } catch (error) {
      if (error.response?.status === 404) {
        const errorDetail = error.response.data.detail;
        
        if (typeof errorDetail === 'object') {
          // Nuevo formato de error con salvedad
          return { 
            success: false, 
            error: errorDetail.error,
            message: errorDetail.message,
            redirect: errorDetail.redirect
          };
        } else {
          // Formato de error anterior
          return { success: false, error: 'Paciente no encontrado' };
        }
      }
      return { success: false, error: 'Error al buscar paciente' };
    }
  },

  // Confirmar turno
  confirmAppointment: async (documento) => {
    try {
      const response = await apiClient.post('/patients/confirm', {
        documento,
        confirmado: true
      });
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: 'Error al confirmar turno' };
    }
  },

  // Obtener todos los pacientes (para admin)
  getAllPatients: async () => {
    try {
      const response = await apiClient.get('/patients/');
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: 'Error al obtener pacientes' };
    }
  },

  // Obtener turnos confirmados
  getConfirmedAppointments: async () => {
    try {
      const response = await apiClient.get('/patients/confirmed/appointments');
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: 'Error al obtener turnos confirmados' };
    }
  }
};

export const serviceAPI = {
  // Registrar solicitud de servicio
  logServiceRequest: async (documento, secretaria, piso) => {
    try {
      const response = await apiClient.post('/services/log', {
        documento,
        secretaria,
        piso
      });
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: 'Error al registrar solicitud' };
    }
  },

  // Obtener estadísticas de servicios
  getServiceStats: async () => {
    try {
      const response = await apiClient.get('/services/stats');
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: 'Error al obtener estadísticas' };
    }
  },

  // Obtener servicios recientes
  getRecentServices: async (limit = 50) => {
    try {
      const response = await apiClient.get(`/services/recent?limit=${limit}`);
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: 'Error al obtener servicios recientes' };
    }
  },

  // Actualizar estado de servicio
  updateServiceStatus: async (serviceId, estado) => {
    try {
      const response = await apiClient.put(`/services/${serviceId}/status`, { estado });
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: 'Error al actualizar estado' };
    }
  }
};

export const healthAPI = {
  // Check API health
  checkHealth: async () => {
    try {
      const response = await apiClient.get('/health');
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: 'API no disponible' };
    }
  }
};

export const secretaryOptions = [
  { id: 'pb', name: 'Secretaría PB', floor: 'Planta Baja' },
  { id: 'pp', name: 'Secretaría PP', floor: 'Primer Piso' },
  { id: '2p', name: 'Secretaría 2P', floor: 'Segundo Piso' },
  { id: '3p', name: 'Secretaría 3P', floor: 'Tercer Piso' }
];

export default apiClient;