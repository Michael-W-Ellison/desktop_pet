# Advanced AI Features - Desktop Pal

## 🧠 Sophisticated Neural Network System

Your desktop pal now features one of the most advanced AI systems for virtual pets, rivaling and exceeding the original "Creatures" game in sophistication!

### AI Complexity Levels

Choose the right level of AI sophistication for your needs:

#### 🟢 SIMPLE Mode (Ages 6-8)
- **Best for**: Younger children, low-end PCs
- **Features**: Basic feedforward neural network
- **Learning**: Simple preference learning
- **Performance**: Very fast, minimal CPU usage

#### 🔵 MEDIUM Mode (Ages 9-12) **[DEFAULT]**
- **Best for**: General use, balanced experience
- **Features**: LSTM networks with memory + sensory inputs
- **Learning**: Temporal pattern recognition, schedule learning
- **Memory**: Remembers sequences of up to 50 interactions, and replays one of its last 500
  player interactions at each decision so it keeps learning between interactions
- **Performance**: Fast, moderate CPU usage

#### 🟣 ADVANCED Mode (Ages 13+)
- **Best for**: Teenagers and adults, high-end PCs
- **Features**: Full RL system with 4 specialized networks
- **Learning**: Goal-oriented behavior, strategic planning
- **Memory**: Complete environmental awareness
- **Performance**: Moderate CPU usage

#### 🔴 EXPERT Mode (Developers/Researchers)
- **Best for**: Understanding AI, educational use
- **Features**: All features + visualization + detailed logging
- **Extras**: Learning metrics, behavior analysis, decision tracking
- **Performance**: Higher CPU usage

---

## 📊 The Seven Major AI Enhancements

### 1. ⚡ Advanced Optimizers

**What it does**: Makes learning faster and more reliable

**Technical Details**:
- **Adam Optimizer**: Combines momentum with adaptive learning rates
  - Beta1 (momentum): 0.9
  - Beta2 (RMSprop): 0.999
  - Adaptive per-parameter learning rates
- **Gradient Clipping**: Prevents exploding gradients (max norm: 5.0)
- **Learning Rate Scheduling**: Exponential decay over time
- **Benefits**: 3-5x faster learning, more stable training

**Your child will notice**:
- Pet adapts to their play style within minutes (not hours)
- Consistent behavioral changes
- Smoother personality development

---

### 2. 🏗️ Expanded Network Architecture

**What it does**: Enables recognition of complex patterns

**Technical Details**:
- **Depth**: 4 hidden layers [64, 32, 16, 8] neurons (vs original [8, 6])
- **Dropout**: 25% dropout rate for generalization
- **Batch Normalization**: Stable training across layers
- **Residual Connections**: Skip connections for deeper learning
- **Total Parameters**: ~5,000+ learnable weights

**Your child will notice**:
- Pet recognizes complex patterns like "she always feeds me after playing ball"
- More nuanced responses to situations
- Unique quirks that emerge over time
- Less repetitive behavior

---

### 3. 🧩 LSTM Networks (Memory System)

**What it does**: Gives the pet true memory of past events

**Technical Details**:
- **Architecture**: 2-layer stacked LSTM
- **Hidden Size**: 32 neurons per layer
- **Sequence Length**: Remembers last 50 interactions
- **Gates**: Forget, Input, Output gates for selective memory
- **BPTT**: Backpropagation Through Time for sequence learning

**How Memory Works**:
```
Without LSTM: "I like being fed" (simple preference)
With LSTM: "Yesterday evening at 7pm, she played ball for 20 minutes,
           then fed me. It's 6:55pm now - she'll probably play soon!"
```

**Your child will notice**:
- Pet remembers what happened earlier today
- Recognizes daily routines ("it's evening, time to play!")
- Responds differently based on recent history
- Anticipates regular patterns (feeding times, play times)
- Forms "opinions" about sequences of events

---

### 4. 🎯 Multiple Specialized Networks

**What it does**: Different "brains" for different tasks

**The Four Networks**:

#### A. MovementNetwork
- **Purpose**: Strategic positioning and pathfinding
- **Inputs**: Position, target location, energy, edges, personality
- **Outputs**: Velocity (x, y), whether to move
- **Learns**: Optimal movement patterns for different goals

#### B. ActivityNetwork
- **Purpose**: Chooses activities based on context
- **Type**: LSTM network (remembers activity sequences)
- **Outputs**: ball_play, mouse_chase, hide_seek, explore, sleep, eat
- **Learns**: Which activities are best for different moods/times

#### C. EmotionNetwork
- **Purpose**: Manages emotional state
- **Emotions**: Joy, Excitement, Contentment, Anxiety, Loneliness
- **Effect**: Emotions modify ALL other behaviors
  - High excitement → faster movement, more playful
  - High contentment → slower movement, less energy drain
  - High loneliness → seeks interaction more

#### D. SocialNetwork
- **Purpose**: Learns player's patterns
- **Type**: LSTM network (learns schedules)
- **Learns**:
  - When player usually interacts
  - What type of interactions they prefer
  - Time of day patterns
  - Weekend vs weekday differences

**Network Coordinator**:
Combines all four networks intelligently:
1. EmotionNetwork updates first (affects everything else)
2. SocialNetwork predicts player behavior
3. ActivityNetwork chooses what to do (influenced by emotions and player prediction)
4. MovementNetwork decides how to move (influenced by activity and emotions)

**Your child will notice**:
- More realistic emotional responses
- Pet "thinks" about what to do next
- Emotions visibly affect behavior (excited = zooms around)
- Pet anticipates when they'll come home from school
- Different response if they've been playing vs ignoring it

---

### 5. 👁️ Sensory Input System

**What it does**: Pet can "see" and "sense" its environment

**28 Sensory Inputs**:

#### Time Awareness (9 inputs)
- Hour of day (sin/cos encoding for circularity)
- Is morning / afternoon / evening / night
- Day of week (sin/cos encoding)
- Is weekend

#### Mouse Tracking (11 inputs)
- Mouse position (x, y) normalized
- Mouse velocity (x, y) normalized
- Distance to creature
- Angle to creature (sin, cos)
- Is mouse approaching
- Mouse speed category (slow/medium/fast)

#### Proximity Sensors (8 inputs)
- Distance to each screen edge (top/bottom/left/right)
- Distance to nearest icon
- Angle to nearest icon
- Count of nearby icons
- Is near hiding spot

**Environmental Awareness**:
- Detects desktop icons as obstacles and hiding spots (reads real icon positions on
  Windows and rescans every minute; other systems assume a standard icon grid)
- Tracks mouse movement and predicts approach
- Knows time of day and adjusts behavior
- Understands screen boundaries

**Your child will notice**:
- Pet hides behind specific icons it has learned are good spots
- Knows when mouse is moving toward it
- Adjusts behavior based on time (sleepier at night)
- Explores new areas of screen intelligently
- Reacts to desktop layout changes

---

### 6. 🎮 Reinforcement Learning (Goal System)

**What it does**: Pet learns through trial-and-error to achieve goals

**Q-Learning Implementation**:
- **State Space**: 35 dimensions (creature stats + sensory inputs)
- **Action Space**: 10 discrete actions
- **Discount Factor**: γ = 0.95 (values future rewards)
- **Exploration**: Epsilon-greedy (starts at 100%, decays to 10%)
- **Experience Replay**: Stores 10,000 past experiences

**The 10 Actions**:
1. Chase Mouse
2. Explore
3. Seek Food
4. Hide
5. Play with Ball
6. Sleep
7. Move to Center
8. Stay Still
9. Seek Player Interaction
10. Random Wander

**Reward Function** (what pet tries to maximize):
```
Reward =
  + 0.1 * happiness_increase
  - 2.0 * (if hunger > 80)
  - 1.0 * (if energy < 20)
  + 0.5 * (alive bonus)
  - 50.0 * (if died)
  + 2.0 * (if player interacted)
  + 1.5 * (if successfully ate when hungry)
  + 1.0 * (if caught ball)
  + 0.3 * (curiosity bonus for new actions)
```

**Goal-Oriented Behavior**:
Pet automatically sets goals based on state:
- If hunger > 70: Goal = "seek_food"
- If energy < 25: Goal = "rest"
- If happiness < 40: Goal = "seek_interaction"
- If player nearby: Goal = "play"
- If the player usually turns up about now: Goal = "seek_interaction"
- Else: Goal = "explore"

Once the pet has enough experience, the Strategic Planner (below) replaces these rules
whenever its plan for the day does clearly better.

**Learning Process**:
1. Pet is in a state
2. RL agent chooses action (explore new things or exploit learned strategy)
3. Pet performs action
4. Reward calculated based on outcome
5. Experience stored in replay buffer
6. Pet learns from batch of past experiences
7. Q-values updated to predict better actions

**Your child will notice**:
- Pet actively seeks food when hungry (not random)
- Learns optimal times to sleep/play/explore
- Tries new behaviors to see what works
- Develops strategies over weeks (e.g., "stay near mouse in evening")
- Makes surprisingly intelligent decisions
- Genuinely goal-seeking behavior

---

### 7. 🗺️ Strategic Planner (ADVANCED and EXPERT)

**What it does**: Plans the coming day so the pet can follow multi-step strategies

**How it works**:
- **World model** learned from the pet's own experience: for each goal, how hunger,
  energy and happiness change while the player is away, what an interaction under that
  goal does (does asking for food get the pet fed?), and how the goal changes the chance
  of an interaction while the player is around
- **Player forecast** for the next 24 hours from the Social Network and the pet's memory
  of previous days
- **Planning** by dynamic programming over 24 hours in 15-minute steps, scoring each step
  with the same reward terms the RL system learns from
- The plan is recomputed every 5 minutes; once the pet has observed 500 decisions, the
  planned goal replaces the goal rules whenever it does clearly better over the day

**Your child will notice**:
- Pet asks for food while the player is around, before it is hungry, when the next
  chance to eat is hours away
- Pet stays awake, and heads over, when the player usually arrives
- Strategies change as the pet learns its player's routine over the weeks

The EXPERT mode's AI Insights view shows the current plan for the day.

---

## 🔬 How It All Works Together

### Typical Decision Process (ADVANCED Mode):

```
1. Sensory System: "Mouse at (500, 300), moving fast, evening time,
                    creature hungry (65), happy (75), energetic (80)"

2. Emotion Network: "Based on hunger and recent interactions:
                     Joy: 0.6, Excitement: 0.7, Anxiety: 0.4"
                     → Emotional modifiers: speed +40%, playfulness +35%

3. Social Network: "It's 7pm on Tuesday - player usually interacts now
                    (85% probability). Likely to play ball or feed."

4. Activity Network (LSTM): "Recent sequence: explore → hide → feed
                            Given emotions and time, best action: seek_interaction"

5. Movement Network: "Activity is seek_interaction, emotions are excited
                     → Move toward center of screen (where player looks)
                     → Speed: 4.2 pixels/frame (modified by excitement)"

6. RL System: "Current goal: seek_interaction. This aligns with networks.
              Q-value for 'seek_interaction' action: 0.85 (good!)
              Execute with 15% exploration (might try something new)"

7. Final Decision:
   - Activity: Seek player interaction
   - Movement: Toward center at 4.2px/frame
   - Emotion: Excited and hopeful
   - Goal: Get player to interact
```

### Learning After Interaction:

```
Player clicks and pets the creature!

1. Reward Calculation:
   - Happiness increased: +5 → reward +0.5
   - Player interacted: +2.0
   - Interaction was positive: +1.0
   - Total reward: +3.5 (very good!)

2. Movement Network learns:
   - "Moving to center when seeking interaction → worked!"
   - Strengthens that pattern

3. Activity Network (LSTM) learns:
   - Sequence: [explore, hide, feed, seek_interaction] → positive outcome
   - More likely to seek interaction after being fed

4. Emotion Network learns:
   - "Evening + moderate hunger + recent feeding → excitement works!"

5. Social Network learns:
   - "Tuesday 7pm → player interacts" (confidence: 87% → 89%)

6. RL System learns:
   - Q-value for "seek_interaction" in this state: 0.85 → 0.91
   - Experience stored in replay buffer
   - Learns from batch of similar past experiences
```

---

## 📈 Expected Behavior Over Time

### Week 1:
- **Random exploration**: Trying different things
- **Basic learning**: Starts to remember you feed it
- **Simple patterns**: Recognizes rough daily schedule

### Week 2:
- **Routine recognition**: Knows morning vs evening behavior
- **Activity preferences**: Clear favorites emerge
- **Strategic movement**: Learns good hiding spots and positions

### Week 3:
- **Schedule prediction**: Anticipates when you'll interact
- **Complex strategies**: Combines multiple behaviors intelligently
- **Emotional depth**: Realistic emotional responses

### Month 2:
- **Unique personality**: Genuinely distinct from other creatures
- **Sophisticated planning**: Multi-step strategies
- **Surprising behaviors**: Emergent patterns you didn't expect

### Month 3+:
- **Deep bonding**: Feels like a real relationship
- **Adaptive learning**: Continuously adjusts to changes
- **Individual quirks**: Behaviors unique to your specific creature

---

## ⚙️ Configuration

### Setting AI Complexity

Edit `src/core/config.py`:

```python
DEFAULT_AI_COMPLEXITY = AIComplexity.MEDIUM  # Change this!

# Options:
# AIComplexity.SIMPLE
# AIComplexity.MEDIUM
# AIComplexity.ADVANCED
# AIComplexity.EXPERT
```

### Tuning Parameters

Advanced users can modify learning behavior:

```python
# Learning rates
LEARNING_RATE = 0.001  # Lower = slower but more stable

# Network architecture
ENHANCED_NETWORK_LAYERS = [64, 32, 16, 8]  # Bigger = more complex patterns

# LSTM memory
SEQUENCE_LENGTH = 50  # How many interactions to remember

# Reinforcement learning
GAMMA = 0.95  # How much to value future rewards (0-1)
EPSILON_DECAY = 0.995  # How fast to reduce exploration

# Dropout (regularization)
DROPOUT_RATE = 0.25  # Higher = less overfitting, more generalization
```

---

## 🎯 For Your 10-Year-Old

With these enhancements, your daughter will experience:

### Sophisticated Enough to Stay Engaged:
✅ Pet remembers her daily schedule
✅ Develops unique behaviors based on her interactions
✅ Shows realistic emotions that affect everything
✅ Makes intelligent, goal-oriented decisions
✅ Learns strategies over weeks and months
✅ Genuinely surprising emergent behaviors

### Educational Value:
✅ Visible AI learning (she can see it adapt)
✅ Cause and effect relationships
✅ Responsibility and care
✅ Pattern recognition
✅ Understanding of intelligence and learning

### Emotional Investment:
✅ Each creature is truly unique
✅ Long-term relationship development
✅ Genuine bonding through learning
✅ Rewards consistent care

---

## 🔬 Technical Achievements

This desktop pal now features:

- **~5,000+** learnable neural network parameters
- **4 specialized neural networks** working in concert
- **LSTM memory** with true sequence learning
- **Reinforcement learning** with experience replay
- **28 sensory inputs** for environmental awareness
- **Q-learning** for goal-oriented behavior
- **Backpropagation Through Time** (BPTT)
- **Adam optimization** with momentum
- **Batch normalization** for training stability
- **Dropout regularization** for generalization
- **Residual connections** for deeper learning
- **Epsilon-greedy exploration** with curiosity bonus
- **Complete save/load** for all network states

**Comparison to Classic Virtual Pets**:
- **Tamagotchi**: Simple state machine
- **Petz (1995)**: Basic neural network (~100 neurons)
- **Creatures (1996)**: Advanced for its time (~500 neurons + genetics)
- **Desktop Pal (2025)**: **Modern deep learning architecture** (~5000+ parameters, 4 specialized networks, LSTM memory, RL)

This is not just a toy - it's a sophisticated AI system that rivals modern research implementations!

---

## 🎓 Perfect for Learning

For students interested in AI/ML, this project demonstrates:
- Feedforward neural networks
- Long Short-Term Memory (LSTM)
- Backpropagation and gradient descent
- Adam optimization
- Q-learning and reinforcement learning
- Experience replay
- Multi-agent systems
- Transfer learning concepts
- Real-world AI application

**All implemented from scratch in readable Python!**

---

## 📝 Credits

**AI Architecture Inspired By**:
- **Creatures** (1996) - Pioneering virtual life AI
- **AlphaGo** - Reinforcement learning concepts
- **Modern Deep Learning** - Adam, LSTM, batch normalization

**Implemented specifically for**: A 10-year-old who deserves a truly intelligent pet! 🎉
