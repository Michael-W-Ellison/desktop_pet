# Desktop Pet - Interactive Virtual Pet

An interactive desktop pet application for Windows that lives on your desktop! Watch as your unique creature hatches from an egg, develops its own personality, and learns from your interactions using neural networks.

## Features

### 🥚 Life Cycle System
- **Egg Stage**: Start with a mysterious egg on your desktop
- **Hatching**: Double-click the egg to hatch your unique creature
- **Growth & Care**: Feed and interact with your pet to keep it happy
- **Death & Rebirth**: If neglected, your creature will pass on and leave a new egg

### 🎨 Procedurally Generated Creatures
- **25 Species**, each with its own pixel-art design: Dragon, Cat, Dog, Bunny, Bird, Fox, Hamster, Owl,
  Penguin, Turtle, plus fantasy creatures (Phoenix, Sprite, Golem, Griffin, Unicorn, Chimera, Wisp, Kraken,
  Hydra, Basilisk, Manticore, Salamander, Sylph, Undine, Gnome)
- **Unique Color Palettes**: Real animals get a natural colouring chosen by the palette; fantasy creatures use it directly
- **8 Personality Types**:
  - **Playful**: Loves to play and interact frequently
  - **Shy**: Prefers hiding and quiet time
  - **Curious**: Explores everything on your desktop
  - **Lazy**: Sleeps often, moves slowly
  - **Energetic**: Always on the move
  - **Mischievous**: Loves moving your icons around
  - **Affectionate**: Follows your mouse cursor
  - **Independent**: Does its own thing

### 🧠 Neural Network Learning
- Your pet learns from every interaction
- Develops preferences based on your play style
- Adapts behavior over time
- Remembers what makes it happy

### 🎮 Interactive Behaviors
- **Mouse Chasing**: Follows your cursor around
- **Ball Playing**: Throw a ball with realistic physics
- **Hide and Seek**: Creature hides behind desktop icons
- **Desktop Exploration**: Wanders around your screen
- **Sleeping**: Rests when energy is low

### 📊 Pet Care System
- **Hunger**: Feed your pet regularly or it will starve
- **Happiness**: Interact to keep your pet happy
- **Energy**: Creatures need rest after playing
- **Statistics**: View detailed stats about your pet

### 🎯 Desktop Integration
- Transparent overlay - pet appears on top of everything
- System tray icon (egg or shelter)
- Right-click menu for quick actions
- Persistent state - your pet remembers everything
- Automatic saving every 5 minutes

## Installation

### Requirements
- Windows 10 or later
- Python 3.7 or higher

### Setup Instructions

1. **Clone or download this repository**
```bash
git clone <repository-url>
cd desktop_pet
```

2. **Install Python dependencies**
```bash
pip install -r requirements.txt
```

3. **Run the application**
```bash
python desktop_pet.py
```

### Creating a Windows Executable (Optional)

To create a standalone .exe file that doesn't require Python:

1. **Install PyInstaller**
```bash
pip install pyinstaller
```

2. **Build the executable**
```bash
pyinstaller --name "DesktopPet" --windowed --onefile --icon=assets/icons/egg.ico desktop_pet.py
```

3. **The executable will be in the `dist` folder**

## How to Use

### Getting Started
1. **Launch the application** - An egg will appear on your desktop
2. **Double-click the egg** to hatch your creature
3. **Meet your new friend!** - You'll see their name, species, and personality

### Interacting with Your Pet

#### Feeding
- Right-click on your pet → Select "Feed"
- Or use the system tray icon → "Feed"
- Feed regularly to prevent starvation!

#### Playing
- **Drag your pet** around the screen with left-click
- **Right-click** → "Play with Ball" to throw a ball
- Your pet will chase and interact with the ball
- Watch as the ball bounces realistically off screen edges

#### Viewing Stats
- Right-click → "Show Stats" to see:
  - Name, species, and personality
  - Age
  - Hunger, happiness, and energy levels
  - Favorite activity

#### System Tray
- The system tray icon shows an **egg** (egg stage) or **shelter** (creature alive)
- Double-click tray icon to show/hide your pet
- Right-click for quick access to actions

### Creature Behaviors

Your pet will autonomously:
- **Wander** around your desktop
- **Chase** your mouse cursor
- **Sleep** when tired
- **Play** with toys
- **Hide** behind icons
- **Explore** the screen

The more you interact, the more your pet learns what you like!

### Care Requirements

⚠️ **Important**: Your pet needs care!

- **Hunger increases** by 0.1 points per minute
- **Feed before hunger reaches 100** or your pet will die
- Even when the app is closed, hunger accumulates
- If you don't open the app for too long, your pet may have passed away

When a creature dies from starvation:
1. A message will inform you of their passing
2. They leave behind an egg
3. The next creature will be completely different!

## Project Structure

```
desktop_pet/
├── src/
│   ├── core/
│   │   ├── config.py           # Configuration and constants
│   │   ├── creature.py         # Creature class with stats and behavior
│   │   ├── neural_network.py  # AI learning system
│   │   ├── persistence.py     # Save/load functionality
│   │   └── pet_manager.py     # Main game logic coordinator
│   ├── ui/
│   │   ├── creature_art.py    # Pixel-art drawing of every species and item
│   │   ├── sprite_generator.py # Sprite sizes, stages, facing and caching
│   │   └── pet_window.py      # Transparent overlay windows
│   ├── utils/
│   └── main.py                # Application entry point
├── assets/
│   ├── creatures/             # (Generated procedurally)
│   ├── icons/
│   └── toys/
├── desktop_pet.py            # Launcher script
├── requirements.txt          # Python dependencies
└── README.md                # This file
```

## Technical Details

### Architecture
- **PyQt5**: GUI framework for transparent windows and system tray
- **PIL/Pillow**: Image generation and manipulation
- **NumPy**: Neural network computations
- **JSON**: Data persistence

### Neural Network
- Feedforward network with configurable layers
- Learns activity preferences from interactions
- Inputs: Hunger, energy, happiness, time since interaction, activity type
- Output: Predicted enjoyment of activities
- Uses backpropagation for online learning

### Physics System
- Realistic ball physics with gravity and bounce
- Collision detection with screen boundaries
- Friction and damping for natural movement

### Sprite Generation
All graphics are **pixel art generated in code** - no image files needed!
- Each species is built from body parts on a 64x64 pixel grid, shaded with five-tone colour ramps,
  light dithering and a coloured outline, and shown at 3x with crisp pixels
- Each evolution stage is drawn on its own grid (a Baby on 32x32), so pixels stay the same size as it grows
- Animated: idle breathing with blinks, a 4-frame walk cycle (a trot on four legs; hopping, waddling,
  floating or slithering for species that move differently), sleeping with closed eyes and rising z's,
  and a wobbling egg; frames are drawn once and cached
- Egg, ball, food bowl, shelter and the application icon are drawn the same way
- Everything drawn with PIL and NumPy

## Customization

### Adjusting Settings
Edit `src/core/config.py` to customize:
- Hunger decay rate
- Creature size
- Animation speed
- Learning rate
- Personality trait modifiers
- And much more!

### Adding New Creature Types
1. Add species name to `CREATURE_TYPES` in `config.py`
2. Add a drawing function decorated with `@species('name')` in `src/ui/creature_art.py`
3. Follow the pattern of existing creature types (body parts in unit coordinates, facing right)

### Adding New Personalities
1. Add to `PersonalityType` enum in `config.py`
2. Define trait modifiers in `PERSONALITY_TRAITS`
3. Customize behavior multipliers

## Troubleshooting

### Pet window not showing
- Check if it's hidden behind other windows
- Try using the system tray icon to show the pet
- The pet might be off-screen - restart the app

### App won't start
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check Python version: `python --version` (needs 3.7+)
- Look for error messages in the console

### Pet died immediately
- Check the save file (`pet_data.json`)
- If corrupted, delete it to start fresh
- Make sure to feed regularly!

### High CPU usage
- Normal during active play (physics simulation)
- Reduces when creature is idle or sleeping
- Adjust FPS in `config.py` if needed

## Credits

Inspired by:
- **Tamagotchi**: The classic virtual pet
- **Creatures**: AI-powered virtual life simulation
- **Shimeji**: Desktop mascot companions

## License

This project is provided as-is for educational and personal use.

## Future Enhancement Ideas

- [ ] Multiple pets at once
- [ ] Pet-to-pet interactions
- [ ] More toy types
- [ ] Custom skins/sprites
- [ ] Sound effects and music
- [ ] Achievements system
- [ ] Cloud save backup
- [ ] Mobile companion app

## Have Fun!

Enjoy bonding with your virtual pet! Remember to check in regularly and keep them fed and happy. Each creature is unique and will develop its own personality based on how you interact with it.

**Happy pet keeping!** 🐾
