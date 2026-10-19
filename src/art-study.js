import './art-study.css';

const variants = {
  coral: { file: 'coral-coast.webp', label: 'A · 珊瑚屋顶 / 湖蓝海水', alt: '局部风格样板：黄墙珊瑚屋顶工作室、树木、岩石、木码头和小帆船，置于湖蓝海水围绕的漂浮岛面。' },
  violet: { file: 'violet-coast.webp', label: 'B · 紫色屋顶 / 鲜蓝海水', alt: '同一局部风格样板的第二版配色：淡紫墙与紫屋顶工作室、树木、岩石、木码头和小帆船，置于鲜蓝海水围绕的漂浮岛面。' },
};

document.querySelectorAll('[data-palette]').forEach(button => {
  button.addEventListener('click', () => {
    const selected = variants[button.dataset.palette];
    document.querySelector('#study-image').src = `${import.meta.env.BASE_URL}art-study/${selected.file}`;
    document.querySelector('#study-image').alt = selected.alt;
    document.querySelector('#study-caption').textContent = `${selected.label}。局部美术样板，尚未替换首页。`;
    document.querySelectorAll('[data-palette]').forEach(other => other.setAttribute('aria-pressed', String(other === button)));
    document.body.dataset.palette = button.dataset.palette;
  });
});
