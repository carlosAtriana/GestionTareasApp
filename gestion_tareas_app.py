import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import json

# Configuración de la base de datos
DATABASE_URL = "sqlite:///tareas.db"
Base = declarative_base()

class Tarea(Base):
    __tablename__ = 'tareas'
    id = Column(Integer, primary_key=True, autoincrement=True)
    titulo = Column(String, nullable=False)
    descripcion = Column(String, nullable=True)
    completada = Column(Boolean, default=False)

# Crear la base de datos y la sesión
engine = create_engine(DATABASE_URL, echo=True)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

# Funciones de la lógica

def agregar_tarea(titulo, descripcion):
    try:
        if not titulo:
            messagebox.showerror("Error", "El título es requerido.")
            return
        if not descripcion:
            messagebox.showerror("Error", "La descripción es requerida.")
            return
        tarea_existente = session.query(Tarea).filter_by(titulo=titulo, descripcion=descripcion).first()
        if tarea_existente:
            messagebox.showerror("Error", "Ya existe una tarea con el mismo contenido.")
            return
        nueva_tarea = Tarea(titulo=titulo, descripcion=descripcion)
        session.add(nueva_tarea)
        session.commit()
        messagebox.showinfo("Éxito", "Tarea agregada exitosamente.")
    except Exception as e:
        session.rollback()
        messagebox.showerror(f"Error", "Error al agregar la tarea. {e}")

def listar_tareas(listbox):
    listbox.delete(0, tk.END)
    tareas = session.query(Tarea).all()
    if tareas:
        for tarea in tareas:
            estado = "[Completada]" if tarea.completada else "[Pendiente]"
            listbox.insert(tk.END, f"ID: {tarea.id} {estado} {tarea.titulo} - {tarea.descripcion}")
    else:
        listbox.insert(tk.END, "No hay tareas registradas.")

def marcar_como_completada(tarea_id):
    try:
        tarea = session.query(Tarea).filter_by(id=int(tarea_id)).first()
        if tarea:
            tarea.completada = True
            session.commit()
            messagebox.showinfo("Éxito", "Tarea marcada como completada.")
        else:
            messagebox.showerror("Error", "Tarea no encontrada.")
    except ValueError:
        messagebox.showerror("Error", "ID inválido.") 
    except Exception as e:
        session.rollback()
        messagebox.showerror(f"Error", f"Error al marcar la tarea como completada. {e}")

def eliminar_tareas_completadas():
    try:
        tareas_completadas = session.query(Tarea).filter_by(completada=True).all()
        if tareas_completadas:
            for tarea in tareas_completadas:
                session.delete(tarea)
            session.commit()
            messagebox.showinfo("Éxito", "Tareas completadas eliminadas.")
        else:
            messagebox.showinfo("Info", "No hay tareas completadas para eliminar.")
    except Exception as e:
        session.rollback()
        messagebox.showerror(f"Error", f"Error al eliminar tareas completadas. {e}")

def guardar_tareas_a_archivo():
    archivo = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("Archivos JSON", "*.json")])
    if archivo:
        tareas = session.query(Tarea).all()
        tareas_json = [
            {"id": tarea.id, "titulo": tarea.titulo, "descripcion": tarea.descripcion, "completada": tarea.completada}
            for tarea in tareas
        ]
        with open(archivo, 'w') as f:
            json.dump(tareas_json, f)
        messagebox.showinfo("Éxito", f"Tareas guardadas en {archivo}.")

def cargar_tareas_desde_archivo():
    archivo = filedialog.askopenfilename(filetypes=[("Archivos JSON", "*.json")])
    if archivo:
        try:
            with open(archivo, 'r') as f:
                tareas_json = json.load(f)
                for tarea in tareas_json:
                    tarea_existente = session.query(Tarea).filter_by(id=tarea['id']).first()
                    if not tarea_existente:
                        nueva_tarea = Tarea(
                            id=tarea['id'],
                            titulo=tarea['titulo'],
                            descripcion=tarea['descripcion'],
                            completada=tarea['completada']
                        )
                        session.add(nueva_tarea)
                session.commit()
            messagebox.showinfo("Éxito", f"Tareas cargadas desde {archivo}.")
        except FileNotFoundError:
            messagebox.showerror("Error", f"El archivo {archivo} no existe.")
        except Exception as e:
            session.rollback()
            messagebox.showerror(f"Error", f"Error al cargar tareas desde {archivo}. {e}")

# Interfaz Gráfica

def main():
    root = tk.Tk()
    root.title("Gestor de Tareas")
    root.geometry("800x600")
    root.resizable(False, False)
    root.iconphoto(False, tk.PhotoImage(file="assets/images.png"))
    


    # Frame para agregar tareas
    frame_agregar = tk.Frame(root)
    frame_agregar.pack(pady=10)

    tk.Label(frame_agregar, text="Título:").grid(row=0, column=0)
    entry_titulo = tk.Entry(frame_agregar)
    entry_titulo.grid(row=0, column=1)

    tk.Label(frame_agregar, text="Descripción:").grid(row=1, column=0)
    entry_descripcion = tk.Entry(frame_agregar)
    entry_descripcion.grid(row=1, column=1)

    btn_agregar = tk.Button(frame_agregar, text="Agregar Tarea", command=lambda: agregar_tarea(entry_titulo.get(), entry_descripcion.get()))
    btn_agregar.grid(row=2, columnspan=2, pady=5)

    # Frame para listar tareas
    frame_listar = tk.Frame(root)
    frame_listar.pack(pady=10)

    listbox_tareas = tk.Listbox(frame_listar, width=80, height=15)
    listbox_tareas.pack()

    btn_listar = tk.Button(frame_listar, text="Listar Tareas", command=lambda: listar_tareas(listbox_tareas))
    btn_listar.pack(pady=5)

    # Frame para acciones
    frame_acciones = tk.Frame(root)
    frame_acciones.pack(pady=10)

    tk.Label(frame_acciones, text="ID Tarea:").grid(row=0, column=0)
    entry_id = tk.Entry(frame_acciones)
    entry_id.grid(row=0, column=1)

    btn_completar = tk.Button(frame_acciones, text="Marcar como Completada", command=lambda: marcar_como_completada(entry_id.get()))
    btn_completar.grid(row=0, column=2, padx=5)

    btn_eliminar = tk.Button(frame_acciones, text="Eliminar Tareas Completadas", command=eliminar_tareas_completadas)
    btn_eliminar.grid(row=1, columnspan=3, pady=5)

    # Frame para guardar y cargar tareas
    frame_archivo = tk.Frame(root)
    frame_archivo.pack(pady=10)

    btn_guardar = tk.Button(frame_archivo, text="Guardar Tareas", command=guardar_tareas_a_archivo)
    btn_guardar.grid(row=0, column=0, padx=5)

    btn_cargar = tk.Button(frame_archivo, text="Cargar Tareas", command=cargar_tareas_desde_archivo)
    btn_cargar.grid(row=0, column=1, padx=5)

    root.mainloop()

if __name__ == "__main__":
    main()
