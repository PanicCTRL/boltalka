import os

tf_path = r'Y:\true_fractal\true_fractal.lua'
with open(tf_path, 'r', encoding='cp1251') as f:
    text = f.read()

# 1. Replace declaration
text = text.replace(
    'fractals     = {}    -- Таблица найденных последних 6 фракталов',
    'fractal_up   = {}    -- Таблица найденных последних верхних фракталов (сопротивления)\nfractal_down = {}    -- Таблица последних нижних фракталов (поддержки)'
)

# 2. Replace dofile
text = text.replace(
    'dofile(getScriptPath() .. "\\\\tf_logic.lua")',
    'dofile(getScriptPath() .. "\\\\split_f_logic.lua")'
)

# 3. Replace LevelCross
old_cross = """function LevelCross()
    if prevPrice == 0 or #fractals == 0 then return end

    virt = VirtualPos()

    if not opn and not virt and count_t == 0 and count_v == 0 then
        startPrice = 0
    end

    for i = 1, #fractals do
        local f = fractals[i]
        local crossUp   = (prevPrice < f and currentPrice >= f)
        local crossDown = (prevPrice > f and currentPrice <= f)

        if crossUp or crossDown then
            if f ~= lastFractal and not opn and not virt then
                LogReset(f)
                startPrice  = f
                lastFractal = f
                count_t     = count_trades
                count_v     = count_trades
            end

            if f == startPrice then
                local direction = crossUp and "СНИЗУ ВВЕРХ" or "СВЕРХУ ВНИЗ"
                LogCross(f, direction)

                if (operation == "B" and crossUp) or (operation == "S" and crossDown) then
                    Trade()
                elseif (operation == "B" and crossDown) or (operation == "S" and crossUp) then
                    OpenVirt()
                end
            end
        end
    end
end"""

new_cross = """function LevelCross()
    if prevPrice == 0 or (#fractal_down == 0 and #fractal_up == 0) then return end

    virt = VirtualPos()

    if not opn and not virt and count_t == 0 and count_v == 0 then
        startPrice = 0
    end

    -- 1. Пробой НИЖНЕГО фрактала (поддержки) СНИЗУ ВВЕРХ -> вход в LONG
    for i = 1, #fractal_down do
        local f = fractal_down[i]
        local crossLowerUp = (prevPrice < f and currentPrice >= f)

        if crossLowerUp then
            if f ~= lastFractal and not opn and not virt then
                LogReset(f)
                startPrice  = f
                lastFractal = f
                count_t     = count_trades
                count_v     = count_trades
            end

            if f == startPrice then
                LogCross(f, "СНИЗУ ВВЕРХ (ОТ НИЖНЕГО ФРАКТАЛА)")
                if not opn and count_t > 0 then
                    Trade()
                end
            end
        end
    end

    -- 2. Пробой ВЕРХНЕГО фрактала (сопротивления) СВЕРХУ ВНИЗ -> вход в SHORT
    for i = 1, #fractal_up do
        local f = fractal_up[i]
        local crossUpperDown = (prevPrice > f and currentPrice <= f)

        if crossUpperDown then
            if f ~= lastFractal and not opn and not virt then
                LogReset(f)
                startPrice  = f
                lastFractal = f
                count_t     = count_trades
                count_v     = count_trades
            end

            if f == startPrice then
                LogCross(f, "СВЕРХУ ВНИЗ (ОТ ВЕРХНЕГО ФРАКТАЛА)")
                if not virt and count_v > 0 then
                    OpenVirt()
                end
            end
        end
    end
end"""

text = text.replace(old_cross.replace('\r\n', '\n'), new_cross.replace('\r\n', '\n'))
text = text.replace(old_cross, new_cross)

# 4. In main loop
old_main = """            local fracStr = table.concat(fractals, ", ")
            
            frc_value = table.concat(fractals, " ")
            if #fractals > 0 then
                FractalTransfer(frc_value)
            end"""

new_main = """            local upStr   = table.concat(fractal_up, ", ")
            local downStr = table.concat(fractal_down, ", ")
            local fracStr = "up=[" .. upStr .. "] down=[" .. downStr .. "]"
            
            frc_value = upStr .. " | " .. downStr
            if #fractal_up > 0 or #fractal_down > 0 then
                FractalTransfer(frc_value)
            end"""

text = text.replace(old_main.replace('\r\n', '\n'), new_main.replace('\r\n', '\n'))
text = text.replace(old_main, new_main)

with open(tf_path, 'w', encoding='cp1251') as f:
    f.write(text)

print('Updated true_fractal.lua successfully')
