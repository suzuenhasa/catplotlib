"""Run this file with an interactive Matplotlib backend for the height slider."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from catplotlib.gallery import code
exec(compile(code('bar'), '<reactive cat scene>', 'exec'))
