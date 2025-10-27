## 🏴‍☠️ Quantum Pirate 3D — *Armada Edition*
> A real-time 3D naval combat simulator built with **Python, Pygame, and PyOpenGL**.
> Sail the high seas, scan for enemy ships, and fire unlimited cannonballs until victory is yours! ⚔️🌊
-----------------------------------------------------------------------------------------------------------------
### 🎮 Features
* 🌊 **Dynamic 3D ocean waves** with procedural animation
* 🚢 **Player and enemy ships** that bob and roll with the waves
* 🏴‍☠️ **Distinct flags** — black for the player, red for enemies
* 💣 **Unlimited cannonballs** — no reloads or firing limits
* 💥 **Explosions, smoke, and splashes** when enemies are hit
* 🛰️ **Radar pulse scanner (Q key)** to detect hidden ships
* 🌟 **Victory screen** with cinematic overlay and glowing text
* 🧭 **Evenly spaced enemy distribution** for balanced gameplay
------------------------------------------------------------------------------------------------------------------
### 🧰 Requirements
Make sure you have **Python 3.8+** and these libraries installed:

pygame, PyOpenGL, numpy

-------------------------------------------------------------------------------------------------------------------
### ▶️ How to Play
1. **Run the game**
In terminal run:
   python quantum_pirate_3d.py
2. **Controls**
   | Action                    | Key               |
   | ------------------------- | ----------------- |
   | Move forward              | `W`               |
   | Move backward             | `S`               |
   | Turn left                 | `A`               |
   | Turn right                | `D`               |
   | Fire cannonball           | Left Mouse Button |
   | Radar pulse               | `Q`               |
   | Quit / Exit after victory | `ESC`             |
3. **Goal** 
   * Use radar (`Q`) to locate enemies.
   * Fire cannonballs to destroy all ships.
   * When the last enemy sinks, you’ll see a glowing **Victory** screen.
------------------------------------------------------------------------------------------------------------
### 🖥️ Technical Details
* Built with **Pygame** for event handling & 2D overlays.
* Uses **PyOpenGL** for rendering the ocean, lighting, and 3D ships.
* Dynamic ocean via sine-wave heightmap simulation.
* Efficient cannonball update loop (no Python list mutation bugs).
* Stable at 60 FPS on most modern systems.
---------------------------------------------------------------------------------------------
### 🧭 Project Structure
```
quantum_pirate_3d.py     # Main game file
README.md                # This file
```
-------------------------------------------------------------------------------------------------------------------------
### 📷 Screenshots
![Screenshot of Quantum Pirate 3D](screenshots/screenshot.png)
----------------------------------------------------------------------------------------------
### 🏆 Credits
**Developed by:** **Team: EntangleX** ⚓
Inspired by classic naval combat and modern particle effects and some theories from the field of the best quantum researchers like SETH LLOYD.
**Libraries:**
* [Pygame](https://www.pygame.org/)
* [PyOpenGL](http://pyopengl.sourceforge.net/)
* [NumPy](https://numpy.org/)
--------------------------------------------------------------------------------------
### 💡 Future Ideas
* 🤖 Enemy ships fire back
* 🌅 Dynamic day/night lighting
* 🌧️ Weather and fog effects
* 🧨 Scoreboard and leaderboard
* 🎵 Sound effects and music
* 🌐 Multiplayer mode over LAN or Internet
* 🌈 Rainbow-colored explosions
* 🌱 More detailed ship models and textures
* 🎯 Targeting reticle and aiming assist
* 🔄 Animated ship animations (e.g., sinking, exploding)
-----------------------------------------------------------------------------------------------------
### 📜 License
This project is open-source and free to use for educational or personal projects.
Just credit *Quantum Pirate 3D — Armada Edition* if you share it. 🏴‍☠️