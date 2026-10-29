(() => {
  const start=document.getElementById('startBtn'),stop=document.getElementById('stopBtn'),status=document.getElementById('recordStatus'),preview=document.getElementById('previewAudio'),fileInput=document.querySelector('#recordingForm input[type=file]');
  if(!start)return;
  let recorder,chunks=[],stream;
  start.onclick=async()=>{
    if(!navigator.mediaDevices?.getUserMedia||!window.MediaRecorder){status.textContent='Browser recording unsupported. Use file upload.';return;}
    try{
      stream=await navigator.mediaDevices.getUserMedia({audio:true});
      const preferred=['audio/webm;codecs=opus','audio/webm','audio/ogg;codecs=opus','audio/mp4'].find(t=>MediaRecorder.isTypeSupported(t));
      recorder=new MediaRecorder(stream,preferred?{mimeType:preferred}:undefined);chunks=[];
      recorder.ondataavailable=e=>{if(e.data.size)chunks.push(e.data)};
      recorder.onstop=()=>{
        const mime=recorder.mimeType||'audio/webm',extension=mime.includes('ogg')?'ogg':mime.includes('mp4')?'m4a':'webm',blob=new Blob(chunks,{type:mime});
        if(blob.size>10*1024*1024){status.textContent='Recording too large (over 10 MB).';return;}
        const file=new File([blob],`voice-${Date.now()}.${extension}`,{type:mime}),dt=new DataTransfer();dt.items.add(file);fileInput.files=dt.files;
        preview.src=URL.createObjectURL(blob);preview.hidden=false;status.textContent='Recording ready. Enter title and language, then click Save Recording.';
      };
      recorder.start();start.disabled=true;stop.disabled=false;status.textContent='🔴 Recording...';
    }catch(err){status.textContent='Microphone unavailable or blocked. Use file upload.';}
  };
  stop.onclick=()=>{if(recorder?.state==='recording')recorder.stop();stream?.getTracks().forEach(t=>t.stop());start.disabled=false;stop.disabled=true};
})();
