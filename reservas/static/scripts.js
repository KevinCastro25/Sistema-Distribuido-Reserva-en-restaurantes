document.addEventListener('DOMContentLoaded', function() {
            // Elementos del DOM
            const reservationDate = document.getElementById('reservation-date');
            const reservationTime = document.getElementById('reservation-time');
            const peopleInput = document.getElementById('people');
            const checkAvailabilityBtn = document.getElementById('check-availability');
            const tablesSection = document.getElementById('tables-section');
            const tablesContainer = document.getElementById('tables-container');
            const errorMessage = document.getElementById('error-message');
            const reservationDetails = document.getElementById('reservation-details');
            const selectedTableNumber = document.getElementById('selected-table-number');
            const selectedTimeSlot = document.getElementById('selected-time-slot');
            const selectedPeople = document.getElementById('selected-people');
            const confirmReservationBtn = document.getElementById('confirm-reservation');
            const cancelSelectionBtn = document.getElementById('cancel-selection');
            const reservationMessage = document.getElementById('reservation-message');
            const phoneInput = document.getElementById('phone');
            
            // Variables de estado
            let selectedTable = null;
            let availableTables = [];
            let selectedDate = '';
            let selectedTime = '';
            
            // Establecer fecha mínima como hoy
            const today = new Date();
            const yyyy = today.getFullYear();
            const mm = String(today.getMonth() + 1).padStart(2, '0');
            const dd = String(today.getDate()).padStart(2, '0');
            const todayStr = `${yyyy}-${mm}-${dd}`;
            reservationDate.setAttribute('min', todayStr);
            
            // Establecer hora actual como mínimo si es hoy
            reservationDate.addEventListener('change', function() {
                if (this.value === todayStr) {
                    const now = new Date();
                    const hours = String(now.getHours()).padStart(2, '0');
                    const minutes = String(now.getMinutes()).padStart(2, '0');
                    reservationTime.setAttribute('min', `${hours}:${minutes}`);
                } else {
                    reservationTime.removeAttribute('min');
                }
            });
            
            // Verificar disponibilidad
            checkAvailabilityBtn.addEventListener('click', function() {
                // Validar fecha y hora
                const date = reservationDate.value;
                const time = reservationTime.value;
                const people = parseInt(peopleInput.value);
                
                if (!date || !time || isNaN(people) || people < 1) {
                    showError('Por favor, complete todos los campos correctamente.');
                    return;
                }
                
                // Validar que no sea una fecha/hora pasada
                const selectedDateTime = new Date(`${date}T${time}`);
                if (selectedDateTime < new Date()) {
                    showError('No se pueden hacer reservas en fechas u horas pasadas.');
                    return;
                }
                
                // Validar que esté dentro del horario permitido (8am-9pm)
                const [hours, minutes] = time.split(':').map(Number);
                if (hours < 8 || (hours === 21 && minutes > 0) || hours > 21) {
                    showError('El horario de reserva debe ser entre 8:00 am y 9:00 pm.');
                    return;
                }
                
                // Ocultar mensajes de error
                hideError();
                
                // Guardar fecha y hora seleccionadas
                selectedDate = date;
                selectedTime = time;
                
                // Consultar disponibilidad
                checkDatabaseAvailability(date, time, people);
            });
            
            // Función para consultar la base de datos
async function checkDatabaseAvailability(date, time, people) {
    try {
        // Obtener todas las mesas
        const response = await fetch('http://127.0.0.1:5000/api/mesas');
        if (!response.ok) {
            showError('Error al consultar las mesas.');
            return;
        }
        const mesas = await response.json();

        // Obtener reservas para la fecha y hora seleccionadas
        const reservasResp = await fetch(`http://127.0.0.1:5000/api/reservas?fecha=${date}&hora=${time}`);
        let reservas = [];
        if (reservasResp.ok) {
            reservas = await reservasResp.json();
        }

        // Filtrar mesas por capacidad
        let disponibles = mesas.filter(m => m.capacidad_Mesa >= people);

        // Marcar mesas reservadas solo si hay solapamiento de horario (90 minutos)
        disponibles = disponibles.map(mesa => {
            // Buscar reservas de esta mesa
            const reservasMesa = reservas.filter(r => r.id_Mesa === mesa.id_Mesa);
            // Verificar si alguna reserva de la mesa solapa con la hora seleccionada
            const tieneSolapamiento = reservasMesa.some(reserva => {
                return haySolapamientoHorario(time, reserva.hora_Reserva);
            });
            return {
                id: mesa.id_Mesa,
                number: mesa.numero_Mesa,
                capacity: mesa.capacidad_Mesa,
                available: !tieneSolapamiento
            };
        });

        availableTables = disponibles;
        displayTables(availableTables);
        tablesSection.classList.remove('hidden');
    } catch (error) {
        showError('Error de conexión con el servidor.');
    }
}
            
            // Función para verificar solapamiento de horarios (1.5 horas de duración)
function haySolapamientoHorario(horaSeleccionada, horaReserva) {
    // Convertir horas a minutos para facilitar la comparación
    const [hSel, mSel] = horaSeleccionada.split(':').map(Number);
    const [hRes, mRes] = horaReserva.split(':').map(Number);
    
    const minutosSel = hSel * 60 + mSel;
    const minutosRes = hRes * 60 + mRes;
    
    // Duración de la reserva en minutos (1.5 horas = 90 minutos)
    const duracion = 90;
    
    // Verificar si los intervalos se solapan
    const solapamiento = !(minutosSel >= minutosRes + duracion || minutosSel + duracion <= minutosRes);
    
    return solapamiento;
}
            
            // Mostrar mesas en la interfaz
function displayTables(tables) {
    tablesContainer.innerHTML = '';
    
    // Contar mesas disponibles
    const mesasDisponibles = tables.filter(table => table.available).length;
    
    if (mesasDisponibles === 0) {
        tablesContainer.innerHTML = `
            <div style="grid-column: 1 / -1; text-align: center; padding: 20px;">
                <p style="margin-bottom: 10px; font-weight: bold;">No hay mesas disponibles para los criterios seleccionados.</p>
                <p>Intenta con otra fecha, hora o número de personas.</p>
            </div>
        `;
        return;
    }
    
    // Ordenar mesas por número
    tables.sort((a, b) => a.number - b.number);
    
    tables.forEach(table => {
        const tableCard = document.createElement('div');
        tableCard.className = `table-card ${table.available ? 'available' : 'reserved'}`;
        
        tableCard.innerHTML = `
            <div class="table-number">Mesa ${table.number}</div>
            <div class="table-status ${table.available ? 'status-available' : 'status-reserved'}">
                ${table.available ? 'Disponible' : 'Reservada'}
            </div>
            <div class="table-capacity">Capacidad: ${table.capacity} personas</div>
        `;
        
        if (table.available) {
            tableCard.style.cursor = 'pointer';
            tableCard.addEventListener('click', () => selectTable(table));
        } else {
            tableCard.style.cursor = 'not-allowed';
            tableCard.style.opacity = '0.7';
        }
        
        tablesContainer.appendChild(tableCard);
    });
}
            
            // Seleccionar una mesa
            function selectTable(table) {
                selectedTable = table;
                
                // Actualizar detalles de reserva
                selectedTableNumber.textContent = table.number;
                selectedTimeSlot.textContent = `${selectedDate} a las ${selectedTime}`;
                selectedPeople.textContent = peopleInput.value;
                
                // Mostrar sección de confirmación
                reservationDetails.classList.remove('hidden');
                
                // Desplazarse a la sección de confirmación
                reservationDetails.scrollIntoView({ behavior: 'smooth' });
            }
            
            // Cancelar selección
            cancelSelectionBtn.addEventListener('click', function() {
                selectedTable = null;
                reservationDetails.classList.add('hidden');
            });
            
            // Confirmar reserva
            confirmReservationBtn.addEventListener('click', function() {
                if (!selectedTable) {
                    showReservationMessage('No se ha seleccionado ninguna mesa.', 'error');
                    return;
                }
                
                // Guardar la reserva en la base de datos
                saveReservationToDatabase();
            });
            
            // Guardar la reserva en la base de datos
            async function saveReservationToDatabase() {
                try {
                    const telefono = phoneInput.value;
                    const response = await fetch('http://127.0.0.1:5000/api/reservas', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            nombre_cliente: 'Invitado',
                            email_cliente: 'invitado@ejemplo.com',
                            telefono_cliente: telefono || 'N/A',
                            id_Mesa: selectedTable.id,
                            fecha_Reserva: selectedDate,
                            hora_Reserva: selectedTime,
                            num_Personas: parseInt(selectedPeople.textContent)
                        })
                    });
                    
                    if (response.ok) {
                        showReservationMessage('¡Reserva confirmada con éxito!', 'success');
                        setTimeout(() => {
                            resetForm();
                        }, 2000);
                    } else {
                        const error = await response.json();
                        showReservationMessage(error.message || 'Error al guardar la reserva.', 'error');
                    }
                } catch (error) {
                    showReservationMessage('Error de conexión con el servidor.', 'error');
                }
            }
            
            // Mostrar mensaje de error
            function showError(message) {
                errorMessage.textContent = message;
                errorMessage.classList.remove('hidden');
            }
            
            // Ocultar mensaje de error
            function hideError() {
                errorMessage.classList.add('hidden');
            }
            
            // Mostrar mensaje de reserva
            function showReservationMessage(message, type) {
                reservationMessage.textContent = message;
                reservationMessage.className = '';
                
                if (type === 'success') {
                    reservationMessage.classList.add('success-message');
                } else {
                    reservationMessage.classList.add('error-message');
                }
                
                reservationMessage.classList.remove('hidden');
            }
            
            // Reiniciar formulario
            function resetForm() {
                reservationDate.value = '';
                reservationTime.value = '';
                peopleInput.value = '';
                phoneInput.value = '';
                
                tablesSection.classList.add('hidden');
                reservationDetails.classList.add('hidden');
                reservationMessage.classList.add('hidden');
                
                selectedTable = null;
            }
        });