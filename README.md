> 📌 **This repository originated from** [here](https://github.com/IntelligentMOtionlab/SNU_ComputerGraphics).

>🔹 The content is **identical** to the original repository.

# Computer Graphics Assignments (2025)

This repository contains the completed code and documentation for the 2025 Computer Graphics programming assignments.

---

## 📦 Contents

- `assignment1_hierarchical_modeling/`: Hierarchical model with animation
- `assignment2_cornell_box/`: Scene modeling of a Cornell box
- `assignment3_roller_coaster/`: Roller coaster simulation using B-splines and arc-length parameterization

---

## 🎮 Assignment #1 — Hierarchical Modeling

**Objective:**  
Design a 3-level hierarchical model using primitive transformations (translation, rotation, scaling), and animate it to show its structure.

**Highlights:**
- Constructed a hierarchical articulated model (e.g., robot arm).
- Used multiple primitive shapes (cubes, cylinders) and transformation matrices.
- Animated joints independently to demonstrate the hierarchy.
- Code written in Pyglet using custom transformation logic.
 
📸 Render: ![Image](https://github.com/user-attachments/assets/06171d9f-8d46-467a-beee-e2dad3327548)

---

## 🧱 Assignment #2 — Cornell Box Scene Modeling

**Objective:**  
Recreate a real-world Cornell Box using geometric primitives and match its physical layout and camera setup in a 3D scene.

**Highlights:**
- Built a box with red, green, and white walls and placed boxes and spheres inside.
- Manually measured dimensions and camera FOV to align virtual and real views.
- Enabled interactive camera via a trackball viewer.
- Includes photo references and matching render screenshots.

📷 Real Photo & 📸 Render Comparison: ![Image](https://github.com/user-attachments/assets/0b22f589-6db3-48cf-93ac-751711a5cf3e)
![Image](https://github.com/user-attachments/assets/6a53ebe8-5356-4a95-9d01-d6c619d91566)
---

## 🎢 Assignment #3 — Roller Coaster Simulation

**Objective:**  
Simulate a moving cart along a smooth spline-based roller coaster track using physically-based motion.

**Highlights:**
- Constructed a closed B-spline loop for the track.
- Implemented arc-length reparameterization to ensure constant-speed motion.
- Defined a Frenet frame (Tangent-Normal-Binormal) moving smoothly along the spline.
- Added realistic motion: speed varies based on track height via energy conservation.
- First-person camera mode implemented to ride the coaster.

📸 Render: ![Image](https://github.com/user-attachments/assets/bf8216ab-614b-450a-8b60-026feb297fb4)
![Image](https://github.com/user-attachments/assets/972f9c43-9cb7-4a59-98a1-1eb57f87a5ad)

