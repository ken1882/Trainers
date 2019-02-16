require "json"

ans = {}
cnt = 0
File.open("ans.txt", 'r') do |file|
  while(line = file.gets)
    next unless line.length > 10
    line = line.split("=>")
    cnt += 1
    key = line[0].gsub(' ', '')
    tmp = line[1].split(' ').collect{|ch| ch.to_i}
    val = []
    idx = 0
    while idx < tmp.size
      if tmp[idx+1] == tmp[idx]
        idx += 2
      end
      val << tmp[idx]
      idx += 1
    end
    ans[key] = val;
  end
end
p cnt
out = ans.to_json
out.gsub!(/,"/, ",\n\"")
File.open("ans_easy.json", 'w') do |file|
  file.write(out)
end