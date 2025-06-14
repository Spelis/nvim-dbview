local M = {}

M.rootpath = vim.fn.fnamemodify(debug.getinfo(1, "S").source:sub(2), ":h")
M.apipath = M.rootpath .. "/api.py"

local default_config = {
	python_path = "python",
	exec_key = "<C-x>",
}

M.config = {}

-- Helper: Run Python script to query DB
function M.query_db(db, query)
	local json = vim.fn.system({ M.config.python_path, M.apipath, "query", db, query })
	return vim.fn.json_decode(json)
end

local function restore_newlines(str)
	return vim.split(str:gsub("%%n", "\n"), "\n")
end

-- Open or reuse a buffer for DB interaction
function M.open(db_path, new_buf)
	if not vim.fn.filereadable(db_path) then
		vim.notify("DB file does not exist: " .. db_path, vim.log.levels.ERROR)
		return
	end
	local buf = new_buf and vim.api.nvim_create_buf(true, true) or vim.api.nvim_get_current_buf()
	if new_buf then
		vim.api.nvim_win_set_buf(0, buf)
	else
		vim.api.nvim_buf_set_lines(buf, 0, -1, false, {})
	end

	vim.bo[buf].swapfile = false
	vim.bo[buf].buftype = "nofile"
	vim.bo[buf].filetype = "sql"
	vim.api.nvim_buf_set_option(buf, "bufhidden", "hide") -- Warn: deprecated
	vim.api.nvim_buf_set_var(buf, "db_path", db_path)
	vim.api.nvim_buf_set_name(buf, "db:" .. vim.fn.sha256(tostring(os.time())))

	vim.api.nvim_win_set_option(0, "conceallevel", 2) -- Warn: deprecated
	vim.api.nvim_buf_call(buf, function()
		vim.cmd([[syntax match ConcealMarker /#/ conceal]])
	end)

	for _, mode in ipairs({ "n", "i", "v" }) do
		vim.keymap.set(mode, M.config.exec_key, M.exec, {
			buffer = buf,
			noremap = true,
			desc = "Execute all queries",
		})
	end
end

-- Execute SQL lines from current buffer and render results
function M.exec()
	local buf = vim.api.nvim_get_current_buf()
	local db = vim.api.nvim_buf_get_var(buf, "db_path")
	local lines = vim.api.nvim_buf_get_lines(buf, 0, -1, false)

	local result_lines = {}

	for _, line in ipairs(lines) do
		if line:match("^%s*#") then
		elseif line:match("%S") then
			table.insert(result_lines, line)

			local trimmed = line:match("^%s*(.-)%s*$")
			local res = M.query_db(db, trimmed)
			local evalquery = res.query
			local command = evalquery:lower():match("^(%w+)") -- Without this aliases that use SELECT wouldn't be recognized, this fixes that.
			local content = ""

			if res.error then
				content = "Error: " .. res.error
				table.insert(result_lines, "# " .. content)
				goto continue
			end

			if command ~= "select" then
				table.remove(result_lines)
				table.insert(result_lines, "#" .. line)
				table.insert(result_lines, "# " .. (res.success and "Query OK" or "Failed"))
				goto continue
			end

			if res.all and #res.all > 0 then
				local is_single_column = type(res.all[1]) == "table" and #res.all[1] == 1

				for _, row in ipairs(res.all) do
					local formatted = is_single_column and tostring(row[1])
						or table.concat(vim.tbl_map(tostring, row), "\t")

					for _, line in ipairs(restore_newlines(formatted)) do
						table.insert(result_lines, "# " .. line)
					end
				end
				goto continue
			end

			-- Fallback: empty result or misc output
			content = "Empty result"
			table.insert(result_lines, "# " .. content)
			::continue::
		else
			table.insert(result_lines, line)
		end
	end

	vim.api.nvim_buf_set_lines(buf, 0, -1, false, result_lines)
end

-- Create new DB files from command or lua
function M.new(db)
	vim.fn.system({ M.config.python_path, M.apipath, "new", db })
end

-- Set up user commands and autocommands
function M.setup(conf)
	M.config = vim.tbl_deep_extend("force", {}, default_config, conf or {})

	vim.api.nvim_create_user_command("DBOpen", function(opts)
		M.open(opts.fargs[1], true)
	end, { nargs = 1 })

	vim.api.nvim_create_user_command("DBNew", function(opts)
		local path = opts.fargs[1]
		M.new(path)
		M.open(path, true)
	end, { nargs = 1 })

	vim.api.nvim_create_user_command("DBQuery", function(opts)
		local query = vim.fn.input({ prompt = "Query: " })
		local result = M.query_db(opts.fargs[1], query)
		vim.fn.setreg("+", vim.inspect(result))
		print(vim.inspect(result))
	end, { nargs = 1 })

	vim.api.nvim_create_autocmd("BufReadPost", {
		pattern = "*.db",
		callback = function(args)
			M.open(vim.api.nvim_buf_get_name(args.buf), false)
		end,
	})
end

M.setup()
return M
