# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Desktop Pet application.

This creates a single-file executable with all dependencies bundled.
Run: pyinstaller desktop_pet.spec
"""

import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Collect all submodules to ensure everything is included
hidden_imports = [
    'PyQt5',
    'PyQt5.QtCore',
    'PyQt5.QtGui',
    'PyQt5.QtWidgets',
    'PIL',
    'PIL.Image',
    'PIL.ImageDraw',
    'PIL.ImageEnhance',
    'PIL.ImageQt',
    'numpy',
    'numpy.core',
    'numpy.core._multiarray_umath',
    # Core modules
    'src.core.config',
    'src.core.creature',
    'src.core.pet_manager',
    'src.core.neural_network',
    'src.core.persistence',
    'src.core.memory_system',
    'src.core.training_system',
    'src.core.evolution_system',
    'src.core.element_system',
    'src.core.variant_system',
    'src.core.bonding_system',
    'src.core.trust_system',
    'src.core.emotional_states',
    'src.core.preference_system',
    'src.core.name_calling',
    'src.core.enhanced_behavior_learner',
    'src.core.reinforcement_learning',
    'src.core.specialized_networks',
    'src.core.lstm_network',
    'src.core.advanced_network',
    'src.core.optimizers',
    'src.core.sensory_system',
    'src.core.personality_system',
    'src.core.biological_needs',
    'src.core.health_system',
    'src.core.aging_system',
    'src.core.breeding_system',
    'src.core.circadian_rhythm',
    'src.core.social_system',
    'src.core.pack_hierarchy',
    'src.core.jealousy_system',
    'src.core.peer_teaching',
    'src.core.animation_system',
    'src.core.sound_system',
    'src.core.music_system',
    'src.core.speech_system',
    'src.core.journal_system',
    'src.core.screenshot_system',
    'src.core.photo_album',
    'src.core.memory_book',
    'src.core.game_base',
    'src.core.fetch_game',
    'src.core.trick_show',
    'src.core.memory_match',
    'src.core.obstacle_course',
    'src.core.game_rewards',
    'src.core.currency_system',
    'src.core.shop_system',
    'src.core.inventory_system',
    'src.core.trading_system',
    'src.core.pet_customization',
    'src.core.room_decoration',
    'src.core.furniture_placement',
    'src.core.furniture_effects',
    'src.core.customization_presets',
    'src.core.interaction_system',
    'src.core.interaction_animations',
    'src.core.autonomous_behavior',
    'src.core.enhanced_memory',
    'src.core.enhanced_training',
    # UI modules
    'src.ui.sprite_generator',
    'src.ui.pet_window',
    'src.ui.particle_effects',
    'src.ui.emotion_particles',
    # Main module
    'src.main',
]

# Automatically collect all submodules from src
all_src_modules = collect_submodules('src')
hidden_imports.extend(all_src_modules)

# Remove duplicates
hidden_imports = list(set(hidden_imports))

a = Analysis(
    ['desktop_pet.py'],
    pathex=[],
    binaries=[],
    datas=[
        # Include the entire src directory
        ('src', 'src'),
        # Include requirements.txt for reference
        ('requirements.txt', '.'),
        ('README.md', '.'),
    ],
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'pandas',
        'scipy',
        'tkinter',
        'test',
        'unittest',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='DesktopPet',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window (GUI app)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icon.ico' if sys.platform == 'win32' else None,
    # Application metadata (Windows only)
    version='version_info.txt' if sys.platform == 'win32' else None,
)
