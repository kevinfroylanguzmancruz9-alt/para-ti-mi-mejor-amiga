import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import random
import math

class RainHeartVideo:
    def __init__(self, width=1280, height=720, fps=30, duration=10):
        self.width = width
        self.height = height
        self.fps = fps
        self.duration = duration
        self.total_frames = fps * duration
        
    def create_heart_mask(self, size=200):
        """Crea una máscara en forma de corazón"""
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Dibujar un coraz��n usando puntos
        points = []
        for t in np.linspace(0, 2*np.pi, 1000):
            x = 16 * np.sin(t)**3
            y = 13 * np.cos(t) - 5 * np.cos(2*t) - 2 * np.cos(3*t) - np.cos(4*t)
            
            # Normalizar coordenadas
            x = int((x + 16) * (size / 32))
            y = int((y + 16) * (size / 32))
            
            if 0 <= x < size and 0 <= y < size:
                points.append((x, y))
        
        # Dibujar el corazón
        if points:
            draw.polygon(points, fill=(255, 0, 0, 255))
        
        return np.array(img)
    
    def generate_rain_drops(self, frame_num, num_drops=500):
        """Genera gotas de lluvia para un frame específico"""
        drops = []
        
        # Usar seed basado en frame para reproducibilidad
        random.seed(frame_num)
        np.random.seed(frame_num)
        
        for _ in range(num_drops):
            x = random.randint(0, self.width)
            y = random.randint(-self.height, self.height)
            speed = random.uniform(5, 15)
            size = random.randint(2, 5)
            opacity = random.randint(100, 255)
            
            drops.append({
                'x': x,
                'y': y,
                'speed': speed,
                'size': size,
                'opacity': opacity
            })
        
        return drops
    
    def is_point_in_heart(self, x, y, heart_center_x, heart_center_y, heart_size):
        """Verifica si un punto está dentro de la forma del corazón"""
        # Ecuación paramétrica del corazón
        dx = x - heart_center_x
        dy = y - heart_center_y
        
        # Normalizar distancia
        scale = heart_size / 2
        dx /= scale
        dy /= scale
        
        # Ecuación del corazón simplificada
        x_normalized = abs(dx)
        y_normalized = dy
        
        # Función del corazón
        heart_value = (x_normalized**2 + (y_normalized - x_normalized**0.5)**2 - 1)
        
        return heart_value <= 0.5
    
    def create_video(self, output_path='rain_heart.mp4'):
        """Crea el video con gotas de lluvia formando un corazón"""
        
        # Configurar VideoWriter
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, self.fps, (self.width, self.height))
        
        heart_center_x = self.width // 2
        heart_center_y = self.height // 2
        heart_size = 250
        
        # Crear máscara del corazón
        heart_mask = self.create_heart_mask(heart_size)
        
        print(f"Generando {self.total_frames} frames...")
        
        for frame_num in range(self.total_frames):
            # Crear frame negro
            frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)
            
            # Generar gotas de lluvia
            drops = self.generate_rain_drops(frame_num, num_drops=300)
            
            # Dibujar gotas
            for drop in drops:
                # Actualizar posición Y con movimiento
                y = (drop['y'] + frame_num * drop['speed']) % (self.height + 200)
                
                # Calcular si está en la forma del corazón
                in_heart = self.is_point_in_heart(
                    drop['x'], 
                    y - self.height // 2, 
                    0, 
                    0, 
                    heart_size
                )
                
                # Color: azul para lluvia en corazón, gris para fuera
                if in_heart:
                    color = (0, 100, 255)  # Rojo en BGR (lluvia dentro del corazón)
                else:
                    color = (100, 100, 100)  # Gris para lluvia normal
                
                # Dibujar gota
                cv2.circle(frame, (int(drop['x']), int(y)), drop['size'], color, -1)
            
            # Dibujar contorno del corazón
            self.draw_heart_outline(frame, heart_center_x, heart_center_y, heart_size)
            
            # Agregar texto "te quiero mucho"
            self.add_text(frame, "te quiero mucho", heart_center_x, heart_center_y + 150)
            
            # Escribir frame
            out.write(frame)
            
            if (frame_num + 1) % 30 == 0:
                print(f"  Procesado frame {frame_num + 1}/{self.total_frames}")
        
        out.release()
        print(f"Video guardado en: {output_path}")
    
    def draw_heart_outline(self, frame, center_x, center_y, size):
        """Dibuja el contorno del corazón"""
        points = []
        for t in np.linspace(0, 2*np.pi, 200):
            x = 16 * np.sin(t)**3
            y = 13 * np.cos(t) - 5 * np.cos(2*t) - 2 * np.cos(3*t) - np.cos(4*t)
            
            # Escalar y trasladar
            x = int(center_x + x * size / 32)
            y = int(center_y - y * size / 32)
            
            points.append([x, y])
        
        points = np.array(points, dtype=np.int32)
        cv2.polylines(frame, [points], True, (255, 100, 100), 2)
    
    def add_text(self, frame, text, x, y):
        """Agrega texto al frame"""
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 1.5
        thickness = 2
        color = (0, 150, 255)  # Rojo en BGR
        
        text_size = cv2.getTextSize(text, font, font_scale, thickness)[0]
        text_x = x - text_size[0] // 2
        text_y = y + text_size[1] // 2
        
        cv2.putText(frame, text, (text_x, text_y), font, font_scale, color, thickness)


# Ejecutar
if __name__ == "__main__":
    # Crear video de 10 segundos, 1280x720, 30 fps
    video_creator = RainHeartVideo(width=1280, height=720, fps=30, duration=10)
    video_creator.create_video('rain_heart.mp4')
    
    print("¡Video creado exitosamente! 💗")