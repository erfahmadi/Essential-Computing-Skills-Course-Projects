set hlsearch
nnoremap <leader>v :vsp<CR>
nnoremap <leader>h :sp<CR>
nnoremap <C-n> :NERDTreeToggle<CR>
nnoremap <leader>w :w<CR>
set number
set relativenumber
set ignorecase
set tabstop=4
set softtabstop=4
syntax enable
colorscheme desert
call plug#begin('~/.vim/plugged')
Plug 'preservim/nerdtree'
Plug 'vim-airline/vim-airline'
call plug#end()


