import os

target_dir = r'Y:\split_fractal'
os.makedirs(target_dir, exist_ok=True)

# 1. sf_logic.lua
sf_logic = '''-- sf_logic.lua
-- Подпрограмма расчета интервалов, экстремумов и фракталов Билла Вильямса
-- с разделением на верхние (fractal_up) и нижние (fractal_down) фракталы

function CheckTimer()
    local current_time = os.time()
    if end_time == 0 then end_time = current_time + period_time end
    if current_time >= end_time then end_time = 0 return true end    
    return false     -- Интервал ещё тикает
end

function UpdateLimits()
    if low_price == 0 then low_price = currentPrice end
    if currentPrice > up_price then up_price = currentPrice end
    if currentPrice < low_price then low_price = currentPrice end
end

function ResetLimits()
    up_price, low_price = 0, 0
end

function FractalTransfer(text)
    local f = io.open(file, "w") 
    if f then
        f:write(text .. "\\n")
        f:close()
    end
end

function PushPrice()
    -- Пропускаем запись, если за интервал не было сделок
    if up_price == 0 then return end

    table.insert(maxPrices, up_price)
    if #maxPrices > 5 then
        table.remove(maxPrices, 1)
    end

    table.insert(minPrices, low_price)
    if #minPrices > 5 then
        table.remove(minPrices, 1)
    end
end

function GetFractal()
    if #maxPrices < 5 or #minPrices < 5 then return end

    -- ФРАКТАЛ ВВЕРХ (сопротивление -> в таблицу fractal_up)
    if maxPrices[3] > maxPrices[1] and maxPrices[3] > maxPrices[2] and 
       maxPrices[3] > maxPrices[4] and maxPrices[3] > maxPrices[5] then
        table.insert(fractal_up, maxPrices[3])
        if #fractal_up > 6 then
            table.remove(fractal_up, 1)
        end
        LogFractal(maxPrices[3], "вверх")
    end

    -- ФРАКТАЛ ВНИЗ (поддержка -> в таблицу fractal_down)
    if minPrices[3] < minPrices[1] and minPrices[3] < minPrices[2] and 
       minPrices[3] < minPrices[4] and minPrices[3] < minPrices[5] then
        table.insert(fractal_down, minPrices[3])
        if #fractal_down > 6 then
            table.remove(fractal_down, 1)
        end
        LogFractal(minPrices[3], "вниз")
    end
end
'''

# 2. sf_logger.lua
sf_logger = '''-- sf_logger.lua
-- Модуль двухуровневого логирования для split_fractal.lua

user_path    = getScriptPath() .. "\\\\sf_user_log.txt"
debug_path   = getScriptPath() .. "\\\\sf_debug_log.txt"

local function GetFracStr()
    if fractals and #fractals > 0 then return table.concat(fractals, ", ") end
    local upStr = (fractal_up and #fractal_up > 0) and ("up=[" .. table.concat(fractal_up, ", ") .. "]") or "up=[]"
    local dnStr = (fractal_down and #fractal_down > 0) and ("down=[" .. table.concat(fractal_down, ", ") .. "]") or "down=[]"
    return upStr .. " " .. dnStr
end

function LogStart()
    local sl_steps = (step and step > 0) and (slOffset / step) or 0
    local tp_steps = (step and step > 0) and (tpOffset / step) or 0

    WriteLog(user_path, "=== ЗАПУСК РОБОТА SPLIT FRACTAL === | period_time = " .. period_time .. "; operation = " .. operation .. "; sec_code = " .. sec_code .. "; quantity = " .. quantity, false)
    WriteLog(user_path, "									| " .. "Стоп = " .. slOffset .. " п, " .. string.format("%.0f", sl_steps) .. " шагов; " .. "Тейк = " .. tpOffset .. " п, " .. string.format("%.0f", tp_steps) .. " шагов.", true)
    WriteLog(debug_path, "=== ЗАПУСК DEBUG SPLIT FRACTAL === | period_time = " .. period_time .. "; operation = " .. operation .. "; sec_code = " .. sec_code, false)
    if FlushLogs then FlushLogs() end
end

function LogStartFractals()
    WriteLog(user_path, "             Загружено фракталов из файла: " .. GetFracStr(), false)
    WriteLog(debug_path, "             Загружено фракталов из файла: " .. GetFracStr(), false)
    if FlushLogs then FlushLogs() end
end

function LogFractal(f, dir)
    WriteLog(debug_path, "              Найден фрактал " .. (dir or "вверх") .. " | f=" .. f .. " fractals=[" .. GetFracStr() .. "]", false)
end

function LogCross(f, direction)
    local dirStr = direction and (" (" .. direction .. ")") or ""
    WriteLog(debug_path, "                Пересечение уровня | f=" .. f .. dirStr .. " prevPrice=" .. prevPrice .. " currentPrice=" .. currentPrice, false)
end

function LogReset(f)
    WriteLog(debug_path, "             Сброс на новый фрактал | new_f=" .. f .. " lastFractal=" .. lastFractal .. " count_t=" .. count_trades .. " count_v=" .. count_trades, false)
end

function LogTradeOpen()
    local fracStr = GetFracStr()
    WriteLog(user_path, "                    Открытие позиции | f=" .. startPrice .. " count_t=" .. count_t, false)
    WriteLog(user_path, "									| fractals=[" .. fracStr .. "]", true)

    local real_stop = (operation == "B") and (startPrice - slOffset) or (startPrice + slOffset)
    local real_take = (operation == "B") and (startPrice + tpOffset) or (startPrice - tpOffset)
    WriteLog(debug_path, "          Открытие реальной сделки | startPrice=" .. startPrice .. " real_stop=" .. real_stop .. " real_take=" .. real_take .. " count_t=" .. count_t, false)
end

function LogVirtOpen()
    WriteLog(debug_path, "       Открытие виртуальной сделки | startPrice=" .. startPrice .. " virt_stop=" .. virt_stop .. " virt_take=" .. virt_take .. " count_v=" .. count_v, false)
end

function LogVirtClose()
    WriteLog(debug_path, "       Закрытие виртуальной сделки | currentPrice=" .. currentPrice .. " virt_stop=" .. virt_stop .. " virt_take=" .. virt_take .. " virt=false", false)
end

function LogOrderSent(op, sec, price_str, qty)
    local opText = (op == "B") and "покупку" or "продажу"
    WriteLog(user_path, string.format("Заявка на %s %s %s в кол-ве %s шт.", opText, sec, price_str, qty), false)
    if FlushLogs then FlushLogs() end
end

function LogBracketSent(op, sec, qty, tp_str, sl_str)
    local opText = (op == "B") and "покупку" or "продажу"
    WriteLog(user_path, string.format("Выставлен брекет на %s %s шт %s. Тейк-профит: %s, Стоп-лосс: %s", opText, qty, sec, tp_str, sl_str), false)
    if FlushLogs then FlushLogs() end
end

function LogStopSent(price_kind, op, qty, sec, stop_str, price_str)
    WriteLog(user_path, string.format("Выставлен %s стоплосс на %s %s шт %s. Цена срабатывания: %s; планка: %s", price_kind, op, qty, sec, stop_str, price_str), false)
    if FlushLogs then FlushLogs() end
end

function LogTransactionError(err_msg)
    WriteLog(user_path, "             Ошибка транзакции. См. сообщение.", true)
    WriteLog(debug_path, "          ОШИБКА ТРАНЗАКЦИИ: " .. tostring(err_msg), true)
    if FlushLogs then FlushLogs() end
end

function LogTradeFill(trade_price, planned_price, qty)
    local slip = math.abs(trade_price - planned_price)
    WriteLog(user_path, string.format("             Исполнен вход: факт=%.1f (план=%.1f | проскальзывание=%.1f п.) | лот=%s", trade_price, planned_price, slip, tostring(qty)), false)
    WriteLog(debug_path, string.format("          Сделка ВХОД | факт=%.1f план=%.1f slip=%.1f qty=%s", trade_price, planned_price, slip, tostring(qty)), false)
    if FlushLogs then FlushLogs() end
end

function LogManualClose(start_p, stop_p)
    WriteLog(user_path, string.format("             [ВЫХОД: РУЧНОЕ ЗАКРЫТИЕ] | startPrice=%s stop_price=%s", tostring(start_p), tostring(stop_p)), true)
    WriteLog(debug_path, string.format("          Ручное закрытие пользователем | startPrice=%s stop_price=%s", tostring(start_p), tostring(stop_p)), false)
    if FlushLogs then FlushLogs() end
end

function LogTradeClose(profit, pnl_pts, pnl_steps)
    local tag = profit and "[ВЫХОД: ТЕЙК-ПРОФИТ]" or "[ВЫХОД: СТОП-ЛОСС]"
    local exit_p = avg_close > 0 and avg_close or currentPrice
    WriteLog(user_path, string.format("             %s | выход=%.1f | прибыль сделки = %+.1f пунктов (%+.1f шагов)", tag, exit_p, pnl_pts, pnl_steps), false)
    WriteLog(user_path, string.format("             прибыль ИТОГО = %+.1f пунктов (%+.1f шагов)", pnl_session_pts, pnl_session_steps), false)
    WriteLog(user_path, string.format("             ИТОГО ДНЕВНАЯ = %+.1f пунктов (%+.1f шагов)", pnl_day_pts, pnl_day_steps), false)
    if FlushLogs then FlushLogs() end
end

function LogStop()
    WriteLog(user_path, "=== ОСТАНОВКА РОБОТА ПОЛЬЗОВАТЕЛЕМ ===", false)
    WriteLog(debug_path, "=== ОСТАНОВКА DEBUG ===", false)
    if FlushLogs then FlushLogs() end
end
'''

# 3. Read other modules from Y:\true_fractal
with open(r'Y:\true_fractal\tf_sendtransaction_spbfut.lua', 'r', encoding='cp1251') as f:
    sf_sendtransaction = f.read().replace('tf_sendtransaction_spbfut.lua', 'sf_sendtransaction_spbfut.lua')

with open(r'Y:\true_fractal\tf_killstop.lua', 'r', encoding='cp1251') as f:
    sf_killstop = f.read().replace('tf_killstop.lua', 'sf_killstop.lua')

with open(r'Y:\true_fractal\tf_read_n_writers.lua', 'r', encoding='cp1251') as f:
    sf_read_n_writers = f.read().replace('tf_read_n_writers.lua', 'sf_read_n_writers.lua')

# 4. split_fractal.lua
with open(r'Y:\true_fractal\true_fractal.lua', 'r', encoding='cp1251') as f:
    split_fractal = f.read()

# Update header and dofile names
split_fractal = split_fractal.replace('-- Главный каркас робота -- true_fractal.lua', '-- Главный каркас робота -- split_fractal.lua')
split_fractal = split_fractal.replace('TrueFractal:', 'SplitFractal:')
split_fractal = split_fractal.replace('\\\\tf_read_n_writers.lua', '\\\\sf_read_n_writers.lua')
split_fractal = split_fractal.replace('\\\\tf_logger.lua', '\\\\sf_logger.lua')
split_fractal = split_fractal.replace('\\\\tf_logic.lua', '\\\\sf_logic.lua')
split_fractal = split_fractal.replace('\\\\split_f_logic.lua', '\\\\sf_logic.lua')
split_fractal = split_fractal.replace('\\\\tf_sendtransaction_spbfut.lua', '\\\\sf_sendtransaction_spbfut.lua')
split_fractal = split_fractal.replace('\\\\tf_killstop.lua', '\\\\sf_killstop.lua')

# Write all files in target_dir in CP1251
files_to_write = {
    'sf_logic.lua': sf_logic,
    'sf_logger.lua': sf_logger,
    'sf_sendtransaction_spbfut.lua': sf_sendtransaction,
    'sf_killstop.lua': sf_killstop,
    'sf_read_n_writers.lua': sf_read_n_writers,
    'split_fractal.lua': split_fractal
}

for fname, content in files_to_write.items():
    fpath = os.path.join(target_dir, fname)
    with open(fpath, 'w', encoding='cp1251') as f:
        f.write(content)
    print(f'Wrote {fpath} (CP1251)')

# Write .gitignore
with open(os.path.join(target_dir, '.gitignore'), 'w', encoding='utf-8') as f:
    f.write('*.txt\n!frc_value.txt\n!pnl_day.txt\n')
print('Wrote .gitignore')

# Write README.md
readme = '''# split_fractal

Робот для терминала QUIK (срочный рынок SPBFUT / Мосбиржа).
Стратегия основана на раздельных очередях верхних (`fractal_up`) и нижних (`fractal_down`) фракталов Билла Вильямса:
- Отскок от пола (пробой нижнего фрактала снизу вверх) -> вход в **LONG**.
- Отбой от потолка (пробой верхнего фрактала сверху вниз) -> вход в **SHORT**.

## Архитектура файлов (Правило 12)
- `split_fractal.lua` — главный файл (каркас, коллбэки, логика `LevelCross`)
- `sf_logic.lua` — таймер, экстремумы и раздельный детект фракталов
- `sf_logger.lua` — двухуровневое логирование (`sf_user_log.txt`, `sf_debug_log.txt`)
- `sf_sendtransaction_spbfut.lua` — исполнение ордеров и брекетов
- `sf_killstop.lua` — снятие активных стоп-заявок
- `sf_read_n_writers.lua` — сохранение и чтение `frc_value.txt` / `pnl_day.txt`
'''

with open(os.path.join(target_dir, 'README.md'), 'w', encoding='utf-8') as f:
    f.write(readme)
print('Wrote README.md')
