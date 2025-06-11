local M = {}

M.apipath = (vim.fn.fnamemodify(debug.getinfo(1, "S").source:sub(2), ":h")) .. "/api.py"

local function init(dtype, db)
	vim.fn.system({ "python", M.apipath, dtype, "new", db })
end

function M.sqlite(db)
	init("sqlite", db)
end

return M
