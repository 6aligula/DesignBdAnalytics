### Información extraída:

#### **YELLOW_TRIP_DATA**
1. **VendorID**:  
   - Tipo: Integer  
   - Longitud: 15  
   - Precisión: 0  

2. **tpep_pickup_datetime**:  
   - Tipo: Date  
   - Formato: yyyy-MM-dd HH:mm:ss  
   - Longitud: 15  
   - Precisión: 0  

3. **tpep_dropoff_datetime**:  
   - Tipo: Date  
   - Formato: yyyy-MM-dd HH:mm:ss  
   - Longitud: 15  
   - Precisión: 0  

4. **passenger_count**:  
   - Tipo: Number  
   - Formato: #.#  
   - Longitud: 3  
   - Precisión: 1  

5. **trip_distance**:  
   - Tipo: Number  
   - Formato: #.#  
   - Longitud: 5  
   - Precisión: 2  

6. **RatecodeID**:  
   - Tipo: Number  
   - Formato: #.#  
   - Longitud: 3  
   - Precisión: 1  

7. **store_and_fwd_flag**:  
   - Tipo: Boolean  

8. **PULocationID**:  
   - Tipo: Integer  
   - Longitud: 15  
   - Precisión: 0  

9. **DOLocationID**:  
   - Tipo: Integer  
   - Longitud: 15  
   - Precisión: 0  

10. **payment_type**:  
    - Tipo: Integer  
    - Longitud: 15  
    - Precisión: 0  

11. **fare_amount**:  
    - Tipo: Number  
    - Formato: #.#  
    - Longitud: 5  
    - Precisión: 1  

12. **extra**:  
    - Tipo: Number  
    - Formato: #.#  
    - Longitud: 4  
    - Precisión: 2  

13. **mta_tax**:  
    - Tipo: Number  
    - Formato: #.#  
    - Longitud: 4  
    - Precisión: 1  

14. **tip_amount**:  
    - Tipo: Number  
    - Formato: #.#  
    - Longitud: 5  
    - Precisión: 2  

15. **tolls_amount**:  
    - Tipo: Number  
    - Formato: #.#  
    - Longitud: 4  
    - Precisión: 2  

16. **improvement_surcharge**:  
    - Tipo: Number  
    - Formato: #.#  
    - Longitud: 4  
    - Precisión: 1  

17. **total_amount**:  
    - Tipo: Number  
    - Formato: #.#  
    - Longitud: 5  
    - Precisión: 2  

18. **congestion_surcharge**:  
    - Tipo: Number  
    - Formato: #.#  
    - Longitud: 4  
    - Precisión: 1  

19. **Airport_fee**:  
    - Tipo: Number  
    - Formato: #.#  
    - Longitud: 4  
    - Precisión: 2  

---

#### **FHV_TRIP_DATA**
1. **dispatching_base_num**:  
   - Tipo: String  
   - Longitud: 6  

2. **pickup_datetime**:  
   - Tipo: Date  
   - Formato: yyyy-MM-dd HH:mm:ss  

3. **dropOff_datetime**:  
   - Tipo: Date  
   - Formato: yyyy-MM-dd HH:mm:ss  

4. **PULocationID**:  
   - Tipo: Integer  
   - Longitud: 15  
   - Precisión: 0 

5. **DOLocationID**:  
   - Tipo: Integer  
   - Longitud: 15  
   - Precisión: 0  

6. **SR_Flag**:  
   - Tipo: Boolean  

7. **Affiliated_base_number**:  
   - Tipo: String  
   - Longitud: 6  

--- 

Ambas tablas representan datos de transporte, siendo **YELLOW_TRIP_DATA** específica para taxis amarillos y **FHV_TRIP_DATA** para servicios de vehículos de alquiler (For-Hire Vehicles). La diferencia clave está en los campos relacionados con los servicios, ubicaciones y tipos de datos requeridos.