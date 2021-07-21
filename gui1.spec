# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(['Code\\gui1.py'],
             pathex=[('C:\\Users\\Xan Ives\\Desktop\\Coding Projects\\[Python] D&D Discord Controller')],
             binaries=[],
             datas= [
                ( 'Code/.env', '.' ),
                ( 'Code/addedButtons.ini', '.' ),
                ( 'Code/readFromFile.py', '.' ),
                ( 'Code/discordTheme.json', '.')
              ],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='gui1',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='gui1')
