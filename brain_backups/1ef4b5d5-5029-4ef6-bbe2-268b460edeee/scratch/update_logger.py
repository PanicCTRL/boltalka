path = r'Y:\true_fractal\tf_logger.lua'
with open(path, 'r', encoding='cp1251') as f:
    text = f.read()

helper = '''local function GetFracStr()
    if fractals and #fractals > 0 then return table.concat(fractals, ", ") end
    local upStr = (fractal_up and #fractal_up > 0) and ("up=[" .. table.concat(fractal_up, ", ") .. "]") or "up=[]"
    local dnStr = (fractal_down and #fractal_down > 0) and ("down=[" .. table.concat(fractal_down, ", ") .. "]") or "down=[]"
    return upStr .. " " .. dnStr
end

'''

if 'local function GetFracStr()' not in text:
    text = text.replace('function LogStart()', helper + 'function LogStart()')
    text = text.replace('table.concat(fractals, ", ")', 'GetFracStr()')

with open(path, 'w', encoding='cp1251') as f:
    f.write(text)

print('Updated tf_logger.lua successfully')
