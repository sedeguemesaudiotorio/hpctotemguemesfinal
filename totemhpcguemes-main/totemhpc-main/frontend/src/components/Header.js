import React from 'react';

const Header = () => {
  return (
    <div className="bg-white px-4 sm:px-6 py-4 rounded-t-lg">
      <div className="flex items-center justify-between flex-wrap gap-2">
        <div className="flex items-center space-x-3">
          <img 
            src="/new_hpc_logo.jpg" 
            alt="HPC Logo" 
            className="h-10 sm:h-12 w-auto" 
            onError={(e) => {
              // Fallback to text if image fails to load
              e.target.style.display = 'none';
              e.target.nextSibling.style.display = 'block';
            }}
          />
          <div className="bg-gray-800 text-white px-2 sm:px-3 py-1 sm:py-2 text-xs sm:text-sm font-bold" style={{display: 'none'}}>
            HPC
          </div>
          <div className="text-gray-700 text-xs sm:text-sm">
            <div className="font-bold">HOSPITAL PRIVADO</div>
            <div>DE COMUNIDAD</div>
          </div>
        </div>
        <div className="text-base sm:text-xl font-bold text-gray-700">
          Terminal de Autogestión
        </div>
      </div>
    </div>
  );
};

export default Header;