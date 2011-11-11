from consts import *
from utils import *

class SWFRawTag(object):
    def __init__(self, s=None):
        if not s is None:
            self.parse(s)

    def parse(self, s):
        pos = s.tell()
        self.header = s.readtag_header()
        self.pos_content = s.tell()
        s.f.seek(pos)
        #self.bytes = s.f.read(self.header.tag_length())
        #s.f.seek(self.pos_content)

class SWFStraightEdge(object):
    def __init__(self, start, to, line_style_idx, fill_style_idx):
        self.start = start
        self.to = to
        self.line_style_idx = line_style_idx
        self.fill_style_idx = fill_style_idx
    
    def reverse_with_new_fillstyle(self, new_fill_idx):
        return SWFStraightEdge(self.to, self.start, self.line_style_idx, new_fill_idx)
        
class SWFCurvedEdge(SWFStraightEdge):
    def __init__(self, start, control, to, line_style_idx, fill_style_idx):
        super(SWFCurvedEdge, self).__init__(start, to, line_style_idx, fill_style_idx)
        self.control = control
        
    def reverse_with_new_fillstyle(self, new_fill_idx):
        return SWFCurvedEdge(self.to, self.control, self.start, self.line_style_idx, new_fill_idx)
     
class SWFShape(object):
    def __init__(self, data=None, level=1, unit_divisor=20.0):
        self._records = []
        self._fillStyles = []
        self._lineStyles = []
        self._postLineStyles = {}
        self._edgeMapsCreated = False
        self.unit_divisor = unit_divisor
        self.fill_edge_maps = []
        self.line_edge_maps = []
        self.current_fill_edge_map = {}
        self.current_line_edge_map = {}
        self.num_groups = 0
        self.coord_map = {}
        if not data is None:
            self.parse(data, level)
            
    def parse(self, data, level=1):
        data.reset_bits_pending()
        fillbits = data.readUB(4)
        linebits = data.readUB(4)
        self.read_shape_records(data, fillbits, linebits, level)
    
    def export(self, handler=None):
        self._create_edge_maps()
        if handler is None:
            handler = SVGShapeExporter()
        handler.begin_shape()
        for i in range(0, self.num_groups):
            self._export_fill_path(handler, i)
            self._export_line_path(handler, i)
        handler.end_shape()
        
    @property
    def records(self):
        return self._records
        
    def read_shape_records(self, data, fill_bits, line_bits, level=1):
        shape_record = None
        record_id = 0
        while type(shape_record) != SWFShapeRecordEnd:
            # The SWF10 spec says that shape records are byte aligned.
            # In reality they seem not to be?
            # bitsPending = 0;
            edge_record = (data.readUB(1) == 1)
            if edge_record:
                straight_flag = (data.readUB(1) == 1)
                num_bits = data.readUB(4) + 2
                if straight_flag:
                    shape_record = data.readSTRAIGHTEDGERECORD(num_bits)
                else:
                    shape_record = data.readCURVEDEDGERECORD(num_bits)
            else:
                states= data.readUB(5)
                if states == 0:
                    shape_record = SWFShapeRecordEnd()
                else:
                    style_change_record = data.readSTYLECHANGERECORD(states, fill_bits, line_bits, level)
                    if style_change_record.state_new_styles:
                        fill_bits = style_change_record.num_fillbits
                        line_bits = style_change_record.num_linebits
                    shape_record = style_change_record
            shape_record.record_id = record_id
            self._records.append(shape_record)
            record_id += 1
            #print shape_record.tostring()
        
    def _create_edge_maps(self):
        if self._edgeMapsCreated:
            return
        xPos = 0
        yPos = 0
        sub_path = []
        fs_offset = 0
        ls_offset = 0
        curr_fs_idx0 = 0
        curr_fs_idx1 = 0
        curr_ls_idx = 0
        
        self.fill_edge_maps = []
        self.line_edge_maps = []
        self.current_fill_edge_map = {}
        self.current_line_edge_map = {}
        self.num_groups = 0
        
        for i in range(0, len(self._records)):
            rec = self._records[i]
            if rec.type == SWFShapeRecord.TYPE_STYLECHANGE:
                if rec.state_line_style or rec.state_fill_style0 or rec.state_fill_style1:
                    if len(sub_path):
                        self._process_sub_path(sub_path, curr_ls_idx, curr_fs_idx0, curr_fs_idx1, rec.record_id)
                    sub_path = []

                if rec.state_new_styles:
                    fs_offset = len(self._fillStyles)
                    ls_offset = len(self._lineStyles)
                    self._append_to(self._fillStyles, rec.fill_styles)
                    self._append_to(self._lineStyles, rec.line_styles)
                
                if rec.state_line_style and rec.state_fill_style0 and rec.state_fill_style1 and \
                    rec.line_style == 0 and rec.fill_style0 == 0 and rec.fill_style1 == 0:
                    # new group (probably)
                    self._clean_edge_map(self.current_fill_edge_map)
                    self._clean_edge_map(self.current_line_edge_map)
                    self.fill_edge_maps.append(self.current_fill_edge_map)
                    self.line_edge_maps.append(self.current_line_edge_map)
                    self.current_fill_edge_map = {}
                    self.current_line_edge_map = {}
                    self.num_groups += 1
                    curr_fs_idx0 = 0
                    curr_fs_idx1 = 0
                    curr_ls_idx = 0
                else:
                    if rec.state_line_style:
                        curr_ls_idx = rec.line_style
                        if curr_ls_idx > 0:
                            curr_ls_idx += ls_offset
                    if rec.state_fill_style0:
                        curr_fs_idx0 = rec.fill_style0
                        if curr_fs_idx0 > 0:
                            curr_fs_idx0 += fs_offset
                    if rec.state_fill_style1:
                        curr_fs_idx1 = rec.fill_style1
                        if curr_fs_idx1 > 0:
                            curr_fs_idx1 += fs_offset
  
                if rec.state_moveto:
                    xPos = rec.move_deltaX
                    yPos = rec.move_deltaY
            elif rec.type == SWFShapeRecord.TYPE_STRAIGHTEDGE:
                start = [NumberUtils.round_pixels_400(xPos), NumberUtils.round_pixels_400(yPos)]
                if rec.general_line_flag:
                    xPos += rec.deltaX
                    yPos += rec.deltaY
                else:
                    if rec.vert_line_flag:
                        yPos += rec.deltaY
                    else:
                        xPos += rec.deltaX
                to = [NumberUtils.round_pixels_400(xPos), NumberUtils.round_pixels_400(yPos)]
                sub_path.append(SWFStraightEdge(start, to, curr_ls_idx, curr_fs_idx1))
            elif rec.type == SWFShapeRecord.TYPE_CURVEDEDGE:
                start = [NumberUtils.round_pixels_400(xPos), NumberUtils.round_pixels_400(yPos)]
                xPosControl = xPos + rec.control_deltaX
                yPosControl = yPos + rec.control_deltaY
                xPos = xPosControl + rec.anchor_deltaX
                yPos = yPosControl + rec.anchor_deltaY
                control = [xPosControl, yPosControl]
                to = [NumberUtils.round_pixels_400(xPos), NumberUtils.round_pixels_400(yPos)]
                sub_path.append(SWFCurvedEdge(start, control, to, curr_ls_idx, curr_fs_idx1))
            elif rec.type == SWFShapeRecord.TYPE_END:
                # We're done. Process the last subpath, if any
                if len(sub_path) > 0:
                    self._process_sub_path(sub_path, curr_ls_idx, curr_fs_idx0, curr_fs_idx1, rec.record_id)
                    self._clean_edge_map(self.current_fill_edge_map)
                    self._clean_edge_map(self.current_line_edge_map)
                    self.fill_edge_maps.append(self.current_fill_edge_map)
                    self.line_edge_maps.append(self.current_line_edge_map)
                    self.current_fill_edge_map = {}
                    self.current_line_edge_map = {}
                    self.num_groups += 1
                curr_fs_idx0 = 0
                curr_fs_idx1 = 0
                curr_ls_idx = 0
    
        self._edgeMapsCreated = True
    
    def _process_sub_path(self, sub_path, linestyle_idx, fillstyle_idx0, fillstyle_idx1, record_id=-1):
        path = None
        if fillstyle_idx0 != 0:
            if not fillstyle_idx0 in self.current_fill_edge_map:
                path = self.current_fill_edge_map[fillstyle_idx0] = []
            else:
                path = self.current_fill_edge_map[fillstyle_idx0]
            for j in range(len(sub_path) - 1, -1, -1):
                path.append(sub_path[j].reverse_with_new_fillstyle(fillstyle_idx0))
                                      
        if fillstyle_idx1 != 0:
            if not fillstyle_idx1 in self.current_fill_edge_map:
                path = self.current_fill_edge_map[fillstyle_idx1] = []
            else:
                path = self.current_fill_edge_map[fillstyle_idx1]
            self._append_to(path, sub_path)
                    
        if linestyle_idx != 0:
            if not linestyle_idx in self.current_line_edge_map:
                path = self.current_line_edge_map[linestyle_idx] = []
            else:
                path = self.current_line_edge_map[linestyle_idx]
            self._append_to(path, sub_path)
             
    def _clean_edge_map(self, edge_map):
        for style_idx in edge_map:
            sub_path = edge_map[style_idx] if style_idx in edge_map else None
            if sub_path is not None and len(sub_path) > 0:
                tmp_path = []
                prev_edge = None
                self._create_coord_map(sub_path)
                while len(sub_path) > 0:
                    idx = 0
                    while idx < len(sub_path):
                        if prev_edge is None or self._equal_point(prev_edge.to, sub_path[idx].start):
                            edge = sub_path[idx]
                            del sub_path[idx]
                            tmp_path.append(edge)
                            self._remove_edge_from_coord_map(edge)
                            prev_edge = edge
                        else:
                            edge = self._find_next_edge_in_coord_map(prev_edge)
                            if not edge is None:
                                idx = sub_path.index(edge)
                            else:
                                idx = 0
                                prev_edge = None
                edge_map[style_idx] = tmp_path
  
    def _equal_point(self, a, b, tol=0.001):
        return (a[0] > b[0]-tol and a[0] < b[0]+tol and a[1] > b[1]-tol and a[1] < b[1]+tol)
    
    def _find_next_edge_in_coord_map(self, edge):
        key = "%0.4f_%0.4f" % (edge.to[0], edge.to[1])
        if key in self.coord_map and len(self.coord_map[key]) > 0:
            return self.coord_map[key][0]
        else:
            return None
             
    def _create_coord_map(self, path):
        self.coord_map = {}
        for i in range(0, len(path)):
            start = path[i].start
            key = "%0.4f_%0.4f" % (start[0], start[1])
            coord_map_array = self.coord_map[key] if key in self.coord_map else None
            if coord_map_array is None:
                self.coord_map[key] = [path[i]]
            else:
                self.coord_map[key].append(path[i])
                
    def _remove_edge_from_coord_map(self, edge):
        key = "%0.4f_%0.4f" % (edge.start[0], edge.start[1])
        if key in self.coord_map:
            coord_map_array = self.coord_map[key]
            if len(coord_map_array) == 1:
                del self.coord_map[key]
            else:
                try:
                    idx = coord_map_array.index(edge)
                    del coord_map_array[idx]
                except:
                    pass
                    
    def _create_path_from_edge_map(self, edge_map):
        new_path = []
        style_ids = []
        for style_id in edge_map:
            style_ids.append(int(style_id))
        style_ids = sorted(style_ids)
        for i in range(0, len(style_ids)):
            self._append_to(new_path, edge_map[style_ids[i]])
        return new_path
        
    def _export_fill_path(self, handler, group_index):
        path = self._create_path_from_edge_map(self.fill_edge_maps[group_index])

        pos = [100000000, 100000000]
        u = 1.0 / self.unit_divisor
        fill_style_idx = 10000000

        if len(path) < 1:
            return
        handler.begin_fills()
        for i in range(0, len(path)):
            e = path[i]
            if fill_style_idx != e.fill_style_idx:
                fill_style_idx = e.fill_style_idx
                pos = [100000000, 100000000]
                try:
                    fill_style = self._fillStyles[fill_style_idx - 1] if fill_style_idx > 0 else None
                    if fill_style.type == 0x0:
                        # solid fill
                        handler.begin_fill(
                            ColorUtils.rgb(fill_style.rgb), 
                            ColorUtils.alpha(fill_style.rgb))
                    elif fill_style.type in [0x10, 0x12, 0x13]:
                        # gradient fill
                        colors = []
                        ratios = []
                        alphas = []
                        for j in range(0, len(fill_style.gradient.records)):
                            gr = fill_style.gradient.records[j]
                            colors.append(ColorUtils.rgb(gr.color))
                            ratios.append(gr.ratio)
                            alphas.append(ColorUtils.alpha(gr.color))
                        handler.begin_gradient_fill(
                            GradientType.LINEAR if fill_style.type == 0x10 else GradientType.RADIAL,
                            colors, alphas, ratios,
                            fill_style.gradient_matrix,
                            fill_style.gradient.spreadmethod,
                            fill_style.gradient.interpolation_mode,
                            fill_style.gradient.focal_point
                            )
                    elif fill_style.type in [0x40, 0x41, 0x42, 0x43]:
                        # bitmap fill
                        handler.begin_bitmap_fill(
                            fill_style.bitmap_id,
                            fill_style.bitmap_matrix,
                            (fill_style.type == 0x40 or fill_style.type == 0x42),
                            (fill_style.type == 0x40 or fill_style.type == 0x41)
                            )
                        pass
                except:
                    # Font shapes define no fillstyles per se, but do reference fillstyle index 1,
                    # which represents the font color. We just report solid black in this case.
                    handler.begin_fill(0)
                        
            if not self._equal_point(pos, e.start):
                handler.move_to(e.start[0] * u, e.start[1] * u)

            if type(e) is SWFCurvedEdge:
                handler.curve_to(e.control[0] * u, e.control[1] * u, e.to[0] * u, e.to[1] * u)
            else:
                handler.line_to(e.to[0] * u, e.to[1] * u)
                
            pos = e.to
  
        handler.end_fill()
        handler.end_fills()
            
    def _export_line_path(self, handler, group_index):
        
        path = self._create_path_from_edge_map(self.line_edge_maps[group_index])
        pos = [100000000, 100000000]
        u = 1.0 / self.unit_divisor
        line_style_idx = 10000000
        line_style = None
        if len(path) < 1:
            return

        handler.begin_lines()
        for i in range(0, len(path)):
            e = path[i]

            if line_style_idx != e.line_style_idx:
                line_style_idx = e.line_style_idx
                pos = [100000000, 100000000]
                try:
                    line_style = self._lineStyles[line_style_idx - 1]
                except:
                    line_style = None
                if line_style is not None:
                    scale_mode = LineScaleMode.NORMAL
                    if line_style.no_hscale_flag and line_style.no_vscale_flag:
                        scale_mode = LineScaleMode.NONE
                    elif line_style.no_hscale_flag:
                        scale_mode = LineScaleMode.HORIZONTAL
                    elif line_style.no_hscale_flag:
                        scale_mode = LineScaleMode.VERTICAL
                    
                    if not line_style.has_fill_flag:
                        handler.line_style(
                            line_style.width / 20.0, 
                            ColorUtils.rgb(line_style.color), 
                            ColorUtils.alpha(line_style.color), 
                            line_style.pixelhinting_flag,
                            scale_mode,
                            line_style.start_caps_style,
                            line_style.end_caps_style,
                            line_style.joint_style,
                            line_style.miter_limit_factor)
                    else:
                        fill_style = line_style.fill_type
                        
                        if fill_style.type in [0x10, 0x12, 0x13]:
                            # gradient fill
                            colors = []
                            ratios = []
                            alphas = []
                            for j in range(0, len(fill_style.gradient.records)):
                                gr = fill_style.gradient.records[j]
                                colors.append(ColorUtils.rgb(gr.color))
                                ratios.append(gr.ratio)
                                alphas.append(ColorUtils.alpha(gr.color))

                            handler.line_gradient_style(
                                line_style.width / 20.0, 
                                line_style.pixelhinting_flag,
                                scale_mode,
                                line_style.start_caps_style,
                                line_style.end_caps_style,
                                line_style.joint_style,
                                line_style.miter_limit_factor,
                                GradientType.LINEAR if fill_style.type == 0x10 else GradientType.RADIAL,
                                colors, alphas, ratios,
                                fill_style.gradient_matrix,
                                fill_style.gradient.spreadmethod,
                                fill_style.gradient.interpolation_mode,
                                fill_style.gradient.focal_point
                                )
                        elif fill_style.type in [0x40, 0x41, 0x42]:
                            handler.line_bitmap_style(
                                line_style.width / 20.0, 
                                line_style.pixelhinting_flag,
                                scale_mode,
                                line_style.start_caps_style,
                                line_style.end_caps_style,
                                line_style.joint_style,
                                line_style.miter_limit_factor,
                                fill_style.bitmap_id, fill_style.bitmap_matrix,
                                (fill_style.type == 0x40 or fill_style.type == 0x42),
                                (fill_style.type == 0x40 or fill_style.type == 0x41)
                                )
                else:
                    # we should never get here
                    handler.line_style(0)
            if not self._equal_point(pos, e.start):
                handler.move_to(e.start[0] * u, e.start[1] * u)
            if type(e) is SWFCurvedEdge:
                handler.curve_to(e.control[0] * u, e.control[1] * u, e.to[0] * u, e.to[1] * u)
            else:
                handler.line_to(e.to[0] * u, e.to[1] * u)
            pos = e.to
        handler.end_lines()
                    
    def _append_to(self, v1, v2):
        for i in range(0, len(v2)):
            v1.append(v2[i])
    
    def __str__(self):
        return "[SWFShape]"
            
class SWFShapeWithStyle(SWFShape):
    def __init__(self, data, level, unit_divisor):
        self._initialFillStyles = []
        self._initialLineStyles = []
        super(SWFShapeWithStyle, self).__init__(data, level, unit_divisor)
    
    def export(self, handler=None):
        self._fillStyles.extend(self._initialFillStyles)
        self._lineStyles.extend(self._initialLineStyles)
        super(SWFShapeWithStyle, self).export(handler)
        
    def parse(self, data, level=1):
        
        data.reset_bits_pending()
        num_fillstyles = self.readstyle_array_length(data, level)
        for i in range(0, num_fillstyles):
            self._initialFillStyles.append(data.readFILLSTYLE(level))
        num_linestyles = self.readstyle_array_length(data, level)
        for i in range(0, num_linestyles):
            if level <= 3:
                self._initialLineStyles.append(data.readLINESTYLE(level))
            else:
                self._initialLineStyles.append(data.readLINESTYLE2(level))
        num_fillbits = data.readUB(4)
        num_linebits = data.readUB(4)
        data.reset_bits_pending()
        self.read_shape_records(data, num_fillbits, num_linebits, level)

    def readstyle_array_length(self, data, level=1):
        length = data.readUI8()
        if level >= 2 and length == 0xff:
            length = data.readUI16()
        return length
    
    def __str__(self):
        s = "    FillStyles:\n" if len(self._fillStyles) > 0 else ""
        for i in range(0, len(self._initialFillStyles)):
            s += "        %d:%s\n" % (i+1, self._initialFillStyles[i].__str__())
        if len(self._initialLineStyles) > 0:
            s += "    LineStyles:\n"
            for i in range(0, len(self._initialLineStyles)):
                s += "        %d:%s\n" % (i+1, self._initialLineStyles[i].__str__())
        for record in self._records:
            s += record.__str__() + '\n'
        return s.rstrip() + super(SWFShapeWithStyle, self).__str__()
              
class SWFShapeRecord(object):
    
    TYPE_UNKNOWN = 0
    TYPE_END = 1
    TYPE_STYLECHANGE = 2
    TYPE_STRAIGHTEDGE = 3
    TYPE_CURVEDEDGE = 4
    
    record_id = -1
    
    def __init__(self, data=None, level=1):
        if not data is None:
            self.parse(data, level)
            
    @property
    def is_edge_record(self):
        return (self.type == SWFShapeRecord.TYPE_STRAIGHTEDGE or 
            self.type == SWFShapeRecord.TYPE_CURVEDEDGE)
            
    def parse(self, data, level=1):
        pass
    
    @property
    def type(self):
        return SWFShapeRecord.TYPE_UNKNOWN
        
    def __str__(self):
        return "    [SWFShapeRecord]"
      			
class SWFShapeRecordStraightEdge(SWFShapeRecord):
    def __init__(self, data, num_bits=0, level=1):
        self.num_bits = num_bits
        super(SWFShapeRecordStraightEdge, self).__init__(data, level)

    def parse(self, data, level=1):
        self.general_line_flag = (data.readUB(1) == 1)
        self.vert_line_flag = False if self.general_line_flag else (data.readUB(1) == 1)
        self.deltaX = data.readSB(self.num_bits) \
            if self.general_line_flag or not self.vert_line_flag \
            else 0.0
        self.deltaY = data.readSB(self.num_bits) \
            if self.general_line_flag or self.vert_line_flag \
            else 0.0
            
    @property
    def type(self):
        return SWFShapeRecord.TYPE_STRAIGHTEDGE

    def __str__(self):
        s = "    [SWFShapeRecordStraightEdge]"
        if self.general_line_flag:
            s += " General: %d %d" % (self.deltaX, self.deltaY)
        else:
            if self.vert_line_flag:
                s += " Vertical: %d" % self.deltaY
            else:
                s += " Horizontal: %d" % self.deltaX
        return s
        
class SWFShapeRecordCurvedEdge(SWFShapeRecord):
    def __init__(self, data, num_bits=0, level=1):
        self.num_bits = num_bits
        super(SWFShapeRecordCurvedEdge, self).__init__(data, level)

    def parse(self, data, level=1):
        self.control_deltaX = data.readSB(self.num_bits)
        self.control_deltaY = data.readSB(self.num_bits)
        self.anchor_deltaX = data.readSB(self.num_bits)
        self.anchor_deltaY = data.readSB(self.num_bits)
        
    @property
    def type(self):
        return SWFShapeRecord.TYPE_CURVEDEDGE

    def __str__(self):
        return "    [SWFShapeRecordCurvedEdge]" + \
            " ControlDelta: %d, %d" % (self.control_deltaX, self.control_deltaY) + \
            " AnchorDelta: %d, %d" % (self.anchor_deltaX, self.anchor_deltaY)
     
class SWFShapeRecordStyleChange(SWFShapeRecord):
    def __init__(self, data, states=0, fill_bits=0, line_bits=0, level=1):
        self.fill_styles = []
        self.line_styles = []
        self.state_new_styles = ((states & 0x10) != 0)
        self.state_line_style = ((states & 0x08) != 0)
        self.state_fill_style1 = ((states & 0x4) != 0)
        self.state_fill_style0 = ((states & 0x2) != 0)
        self.state_moveto = ((states & 0x1) != 0)
        self.num_fillbits = fill_bits
        self.num_linebits = line_bits
        self.move_deltaX = 0.0
        self.move_deltaY = 0.0
        self.fill_style0 = 0
        self.fill_style1 = 0
        self.line_style = 0
        super(SWFShapeRecordStyleChange, self).__init__(data, level)

    def parse(self, data, level=1):
        
        if self.state_moveto:
            movebits = data.readUB(5)
            self.move_deltaX = data.readSB(movebits)
            self.move_deltaY = data.readSB(movebits)
        self.fill_style0 = data.readUB(self.num_fillbits) if self.state_fill_style0 else 0
        self.fill_style1 = data.readUB(self.num_fillbits) if self.state_fill_style1 else 0
        self.line_style = data.readUB(self.num_linebits) if self.state_line_style else 0
        if self.state_new_styles:
            data.reset_bits_pending();
            num_fillstyles = self.readstyle_array_length(data, level)
            for i in range(0, num_fillstyles):
                self.fill_styles.append(data.readFILLSTYLE(level))
            num_linestyles = self.readstyle_array_length(data, level)
            for i in range(0, num_linestyles):
                if level <= 3:
                    self.line_styles.append(data.readLINESTYLE(level))
                else:
                    self.line_styles.append(data.readLINESTYLE2(level))
            self.num_fillbits = data.readUB(4)
            self.num_linebits = data.readUB(4)
            
    @property
    def type(self):
        return SWFShapeRecord.TYPE_STYLECHANGE
    
    def readstyle_array_length(self, data, level=1):
        length = data.readUI8()
        if level >= 2 and length == 0xff:
            length = data.readUI16()
        return length
            
    def __str__(self):
        return "    [SWFShapeRecordStyleChange]" + \
            " moveTo: %d %d" % (self.move_deltaX, self.move_deltaY) + \
            " fs0: %d" % self.fill_style0 + \
            " fs1: %d" % self.fill_style1 + \
            " linestyle: %d" % self.line_style + \
            " flags: %d %d %d" % (self.state_fill_style0, self.state_fill_style1, self.state_line_style)
                                   
class SWFShapeRecordEnd(SWFShapeRecord):
    def __init__(self):
        super(SWFShapeRecordEnd, self).__init__(None)
        
    def parse(self, data, level=1):
        pass

    @property
    def type(self):
        return SWFShapeRecord.TYPE_END

    def __str__(self):
        return "    [SWFShapeRecordEnd]"
                
class SWFMatrix(object):
    def __init__(self, data):
        self.scaleX = 1.0
        self.scaleY = 1.0
        self.rotateSkew0 = 0.0
        self.rotateSkew1 = 0.0
        self.translateX = 0.0
        self.translateY = 0.0
        if not data is None:
            self.parse(data)
            
    def parse(self, data):
        data.reset_bits_pending();
        self.scaleX = 1.0
        self.scaleY = 1.0
        if data.readUB(1) == 1:
            scaleBits = data.readUB(5)
            self.scaleX = data.readFB(scaleBits)
            self.scaleY = data.readFB(scaleBits)
        self.rotateSkew0 = 0.0
        self.rotateSkew1 = 0.0
        if data.readUB(1) == 1:
            rotateBits = data.readUB(5)
            self.rotateSkew0 = data.readFB(rotateBits)
            self.rotateSkew1 = data.readFB(rotateBits)
        translateBits = data.readUB(5)
        self.translateX = data.readSB(translateBits)
        self.translateY = data.readSB(translateBits)
    
    def to_array(self):
        return [
            self.scaleX, self.rotateSkew0, 
            self.rotateSkew1, self.scaleY, 
            self.translateX, self.translateY
        ]
    
    def __str__(self):
        def fmt(s):
            return "%0.2f" % s
            
        return "[%s]" % ",".join(map(fmt, self.to_array()))
        
class SWFGradientRecord(object):
    def __init__(self, data=None, level=1):
        self._records = []
        if not data is None:
            self.parse(data, level)

    def parse(self, data, level=1):  
        self.ratio = data.readUI8()
        self.color = data.readRGB() if level <= 2 else data.readRGBA()
    
    def __str__(self):
        return "[SWFGradientRecord] Color: %s, Ratio: %d" % (ColorUtils.to_rgb_string(self.color), self.ratio)
        
class SWFGradient(object):
    def __init__(self, data=None, level=1):
        self._records = []
        self.focal_point = 0.0
        if not data is None:
            self.parse(data, level)
    
    @property
    def records(self):
        return self._records
        
    def parse(self, data, level=1):  
        data.reset_bits_pending();
        self.spreadmethod = data.readUB(2)
        self.interpolation_mode = data.readUB(2)
        num_gradients = data.readUB(4)
        for i in range(0, num_gradients):
            self._records.append(data.readGRADIENTRECORD(level))
    
    def __str__(self):
        s = "[SWFGadient]"
        for record in self._records:
            s += "\n  " + record.__str__()
        return s
        
class SWFFocalGradient(SWFGradient):
    def __init__(self, data=None, level=1):
        super(SWFFocalGradient, self).__init__(data, level)

    def parse(self, data, level=1):  
        super(SWFFocalGradient, self).parse(data, level)
        self.focal_point = data.readFIXED8()
    
    def __str__(self):
        return "[SWFFocalGradient] Color: %s, Ratio: %d, Focal: %0.2f" % \
            (ColorUtils.to_rgb_string(self.color), self.ratio, self.focal_point)
                                      
class SWFFillStyle(object):
    def __init__(self, data=None, level=1):
        if not data is None:
            self.parse(data, level)
            
    def parse(self, data, level=1):
        self.type = data.readUI8()
        if self.type == 0x0:
            self.rgb = data.readRGB() if level <= 2 else data.readRGBA()
        elif self.type in [0x10, 0x12, 0x13]:
            self.gradient_matrix = data.readMATRIX()
            self.gradient = data.readFOCALGRADIENT(level) if self.type == 0x13 else data.readGRADIENT(level)
        elif self.type in [0x40, 0x41, 0x42, 0x43]:
            self.bitmap_id = data.readUI16()
            self.bitmap_matrix = data.readMATRIX()
        else:
            raise Exception("Unknown fill style type: 0x%x" % self.type, level)
    
    def __str__(self):
        s = "[SWFFillStyle] "
        if self.type == 0x0:
            s += "Color: %s" % ColorUtils.to_rgb_string(self.rgb)
        elif self.type in [0x10, 0x12, 0x13]:
            s += "Gradient: %s" % self.gradient_matrix
        elif self.type in [0x40, 0x41, 0x42, 0x43]:
            s += "BitmapID: %d" % (self.bitmap_id)
        return s
        
class SWFLineStyle(object):
    def __init__(self, data=None, level=1):
        # forward declarations for SWFLineStyle2
        self.start_caps_style = LineCapsStyle.ROUND
        self.end_caps_style = LineCapsStyle.ROUND
        self.joint_style = LineJointStyle.ROUND
        self.has_fill_flag = False
        self.no_hscale_flag = False
        self.no_vscale_flag = False
        self.pixelhinting_flag = False
        self.no_close = False
        self.miter_limit_factor = 3.0
        self.fill_type = None
        self.width = 1
        self.color = 0
        if not data is None:
            self.parse(data, level)

    def parse(self, data, level=1):
        self.width = data.readUI16()
        self.color = data.readRGB() if level <= 2 else data.readRGBA()
    
    def __str__(self):
        s = "[SWFLineStyle] "
        s += "Color: %s, Width: %d" % (ColorUtils.to_rgb_string(self.color), self.width)
        return s
                          
class SWFLineStyle2(SWFLineStyle):
    def __init__(self, data=None, level=1):
        super(SWFLineStyle2, self).__init__(data, level)

    def parse(self, data, level=1):
        self.width = data.readUI16()
        self.start_caps_style = data.readUB(2)
        self.joint_style = data.readUB(2)
        self.has_fill_flag = (data.readUB(1) == 1)
        self.no_hscale_flag = (data.readUB(1) == 1)
        self.no_vscale_flag = (data.readUB(1) == 1)
        self.pixelhinting_flag = (data.readUB(1) == 1)
        data.readUB(5)
        self.no_close = (data.readUB(1) == 1)
        self.end_caps_style = data.readUB(2)
        if self.joint_style == LineJointStyle.MITER:
            self.miter_limit_factor = data.readFIXED8()
        if self.has_fill_flag:
            self.fill_type = data.readFILLSTYLE(level)
        else:
            self.color = data.readRGBA()

    def __str__(self):
        s = "[SWFLineStyle2] "
        s += "Width: %d, " % self.width
        s += "StartCapsStyle: %d, " % self.start_caps_style
        s += "JointStyle: %d, " % self.joint_style
        s += "HasFillFlag: %d, " % self.has_fill_flag
        s += "NoHscaleFlag: %d, " % self.no_hscale_flag
        s += "NoVscaleFlag: %d, " % self.no_vscale_flag
        s += "PixelhintingFlag: %d, " % self.pixelhinting_flag
        s += "NoClose: %d, " % self.no_close
        
        if self.joint_style:
            s += "MiterLimitFactor: %d" % self.miter_limit_factor
        if self.has_fill_flag:
            s += "FillType: %s, " % self.fill_type
        else:
            s += "Color: %s" % ColorUtils.to_rgb_string(self.color)
        
        return s

class SWFMorphGradientRecord(object):
    def __init__(self, data):
        if not data is None:
            self.parse(data)
            
    def parse(self, data):
        self.startRatio = data.readUI8()
        self.startColor = data.readRGBA()
        self.endRatio = data.readUI8()
        self.endColor = data.readRGBA()

class SWFMorphGradient(object):
    def __init__(self, data, level=1):
        self.records = []
        if not data is None:
            self.parse(data, level)
            
    def parse(self, data, level=1):
        self.records = []
        numGradients = data.readUI8()
        for i in range(0, numGradients):
            self.records.append(data.readMORPHGRADIENTRECORD())
            
class SWFMorphFillStyle(object):
    def __init__(self, data, level=1):
        if not data is None:
            self.parse(data, level)
            
    def parse(self, data, level=1):
        type = data.readUI8()
        if type == 0x0:
            self.startColor = data.readRGBA()
            self.endColor = data.readRGBA()
        elif type in [0x10, 0x12]:
            self.startGradientMatrix = data.readMATRIX()
            self.endGradientMatrix = data.readMATRIX()
            self.gradient = data.readMORPHGRADIENT(level)
        elif type in [0x40, 0x41, 0x42, 0x43]:
            self.bitmapId = data.readUI16()
            self.startBitmapMatrix = data.readMATRIX()
            self.endBitmapMatrix = data.readMATRIX()

class SWFMorphLineStyle(object):
    def __init__(self, data, level=1):
        # Forward declaration of SWFMorphLineStyle2 properties
        self.startCapsStyle = LineCapsStyle.ROUND
        self.endCapsStyle = LineCapsStyle.ROUND
        self.jointStyle = LineJointStyle.ROUND
        self.hasFillFlag = False
        self.noHScaleFlag = False
        self.noVScaleFlag = False
        self.pixelHintingFlag = False
        self.noClose = False
        self.miterLimitFactor = 3
        self.fillType = None
        if not data is None:
            self.parse(data, level)

    def parse(self, data, level=1):
        self.startWidth = data.readUI16()
        self.endWidth = data.readUI16()
        self.startColor = data.readRGBA()
        self.endColor = data.readRGBA()

class SWFMorphLineStyle2(SWFMorphLineStyle):
    def __init__(self, data, level=1):
        super(SWFMorphLineStyle2, self).__init__(data, level)

    def parse(self, data, level=1):
        self.startWidth = data.readUI16()
        self.endWidth = data.readUI16()
        self.startCapsStyle = data.readUB(2)
        self.jointStyle = data.readUB(2)
        self.hasFillFlag = (data.readUB(1) == 1)
        self.noHScaleFlag = (data.readUB(1) == 1)
        self.noVScaleFlag = (data.readUB(1) == 1)
        self.pixelHintingFlag = (data.readUB(1) == 1)
        reserved = data.readUB(5);
        self.noClose = (data.readUB(1) == 1)
        self.endCapsStyle = data.readUB(2)
        if self.jointStyle == LineJointStyle.MITER:
            self.miterLimitFactor = data.readFIXED8()
        if self.hasFillFlag:
            self.fillType = data.readMORPHFILLSTYLE(level)
        else:
            self.startColor = data.readRGBA()
            self.endColor = data.readRGBA()

class SWFRecordHeader(object):
    def __init__(self, type, content_length, header_length):
        self.type = type
        self.content_length = content_length
        self.header_length = header_length

    @property
    def tag_length(self):
        return self.header_length + self.content_length

class SWFRectangle(object):
    def __init__(self):
        self.xmin = self.xmax = self.ymin = self.ymax = 0

    def parse(self, s):
        s.reset_bits_pending()
        bits = s.readUB(5)
        self.xmin = s.readSB(bits)
        self.xmax = s.readSB(bits)
        self.ymin = s.readSB(bits)
        self.ymax = s.readSB(bits)

    def __str__(self):
        return "[xmin: %d xmax: %d ymin: %d ymax: %d]" % (self.xmin/20, self.xmax/20, self.ymin/20, self.ymax/20)
        
class SWFColorTransform(object):
    def __init__(self, data=None):
        if not data is None:
            self.parse(data)
    
    def parse(self, data):
        data.reset_bits_pending()
        self.hasAddTerms = (data.readUB(1) == 1)
        self.hasMultTerms = (data.readUB(1) == 1)
        bits = data.readUB(4)
        self.rMult = 1
        self.gMult = 1
        self.bMult = 1
        if self.hasMultTerms:
            self.rMult = data.readSB(bits)
            self.gMult = data.readSB(bits)
            self.bMult = data.readSB(bits)
        self.rAdd = 0
        self.gAdd = 0
        self.bAdd = 0
        if self.hasAddTerms:
            self.rAdd = data.readSB(bits)
            self.gAdd = data.readSB(bits)
            self.bAdd = data.readSB(bits)
    
    @property
    def matrix(self):
        return [
            self.rMult / 256.0, 0.0, 0.0, 0.0, self.rAdd / 256.0,
            0.0, self.gMult / 256.0, 0.0, 0.0, self.gAdd / 256.0,
            0.0, 0.0, self.bMult / 256.0, 0.0, self.bAdd / 256.0,
            0.0, 0.0, 0.0, 1.0, 1.0
        ]
        
    def __str__(self):
        return "[%d %d %d %d %d %d]" % \
            (self.rMult, self.gMult, self.bMult, self.rAdd, self.gAdd, self.bAdd)
        
class SWFColorTransformWithAlpha(SWFColorTransform):
    def __init__(self, data=None):
        super(SWFColorTransformWithAlpha, self).__init__(data)

    def parse(self, data):
        data.reset_bits_pending()
        self.hasAddTerms = (data.readUB(1) == 1)
        self.hasMultTerms = (data.readUB(1) == 1)
        bits = data.readUB(4)
        self.rMult = 1
        self.gMult = 1
        self.bMult = 1
        self.aMult = 1
        if self.hasMultTerms:
            self.rMult = data.readSB(bits)
            self.gMult = data.readSB(bits)
            self.bMult = data.readSB(bits)
            self.aMult = data.readSB(bits)     
        self.rAdd = 0
        self.gAdd = 0
        self.bAdd = 0
        self.aAdd = 0
        if self.hasAddTerms:
            self.rAdd = data.readSB(bits)
            self.gAdd = data.readSB(bits)
            self.bAdd = data.readSB(bits)
            self.aAdd = data.readSB(bits)
    
    @property
    def matrix(self):
        '''
        Gets the matrix as a 20 item list
        '''
        return [
            self.rMult / 256.0, 0.0, 0.0, 0.0, self.rAdd / 256.0,
            0.0, self.gMult / 256.0, 0.0, 0.0, self.gAdd / 256.0,
            0.0, 0.0, self.bMult / 256.0, 0.0, self.bAdd / 256.0,
            0.0, 0.0, 0.0, self.aMult / 256.0, self.aAdd / 256.0
        ]
                
    def __str__(self):
        return "[%d %d %d %d %d %d %d %d]" % \
            (self.rMult, self.gMult, self.bMult, self.aMult, self.rAdd, self.gAdd, self.bAdd, self.aAdd)
 
class SWFFrameLabel(object):
    def __init__(self, frameNumber, name):
        self.frameNumber = frameNumber
        self.name = name

    def __str__(self):
        return "Frame: %d, Name: %s" % (self.frameNumber, self.name)
                               
class SWFScene(object):
    def __init__(self, offset, name):
        self.offset = offset
        self.name = name
        
    def __str__(self):
        return "Scene: %d, Name: '%s'" % (self.offset, self.name)
        
class SWFSymbol(object):
    def __init__(self, data=None):
        if not data is None:
            self.parse(data)
        
    def parse(self, data):
        self.tagId = data.readUI16()
        self.name = data.readString()

    def __str__(self):
        return "ID %d, Name: %s" % (self.tagId, self.name)
        
class SWFGlyphEntry(object):
    def __init__(self, data=None, glyphBits=0, advanceBits=0):
        if not data is None:
            self.parse(data, glyphBits, advanceBits)
        
    def parse(self, data, glyphBits, advanceBits):
        # GLYPHENTRYs are not byte aligned
        self.index = data.readUB(glyphBits)
        self.advance = data.readSB(advanceBits)
    
    def __str__(self):
        return "Index: %d, Advance: %d" % (self.index, self.advance)
        
class SWFKerningRecord(object):
    def __init__(self, data=None, wideCodes=False):
        if not data is None:
            self.parse(data, wideCodes)
        
    def parse(self, data, wideCodes):
        self.code1 = data.readUI16() if wideCodes else data.readUI8()
        self.code2 = data.readUI16() if wideCodes else data.readUI8()
        self.adjustment = data.readSI16()
    
    def __str__(self):
        return "Code1: %d, Code2: %d, Adjustement: %d" % (self.code1, self.code2, self.adjustment)
        
class SWFTextRecord(object):
    def __init__(self, data=None, glyphBits=0, advanceBits=0, previousRecord=None, level=1):
        self.hasFont = False
        self.hasColor = False
        self.hasYOffset = False
        self.hasXOffset = False
        self.fontId = -1
        self.textColor = 0
        self.xOffset = 0
        self.yOffset = 0
        self.textHeight = 12
        self.glyphEntries = []
        if not data is None:
            self.parse(data, glyphBits, advanceBits, previousRecord, level)

    def parse(self, data, glyphBits, advanceBits, previousRecord=None, level=1):
        self.glyphEntries = []
        styles = data.readUI8()
        self.type = styles >> 7
        self.hasFont = ((styles & 0x08) != 0)
        self.hasColor = ((styles & 0x04) != 0)
        self.hasYOffset = ((styles & 0x02) != 0)
        self.hasXOffset = ((styles & 0x01) != 0)
        
        if self.hasFont:
            self.fontId = data.readUI16()
        elif not previousRecord is None:
            self.fontId = previousRecord.fontId
        
        if self.hasColor:
            self.textColor = data.readRGB() if level < 2 else data.readRGBA()
        elif not previousRecord is None:
            self.textColor = previousRecord.textColor
        
        if self.hasXOffset:
            self.xOffset = data.readSI16();
        elif not previousRecord is None:
            self.xOffset = previousRecord.xOffset
        
        if self.hasYOffset:
            self.yOffset = data.readSI16();
        elif not previousRecord is None:
            self.yOffset = previousRecord.yOffset
        
        if self.hasFont:
            self.textHeight = data.readUI16()
        elif not previousRecord is None:
            self.textHeight = previousRecord.textHeight
        
        glyphCount = data.readUI8()
        for i in range(0, glyphCount):
            self.glyphEntries.append(data.readGLYPHENTRY(glyphBits, advanceBits))
    
    def __str__(self):
        return "[SWFTextRecord]"
        
class SWFClipActions(object):
    def __init__(self, data=None, version=0):
        self.eventFlags = None
        self.records = []
        if not data is None:
            self.parse(data, version)

    def parse(self, data, version):
        data.readUI16() # reserved, always 0
        self.eventFlags = data.readCLIPEVENTFLAGS(version)
        self.records = []
        record = data.readCLIPACTIONRECORD(version)
        while not record is None:
            self.records.append(record)
            record = data.readCLIPACTIONRECORD(version)

    def __str__(self):
        return "[SWFClipActions]"
                         
class SWFClipActionRecord(object):
    def __init__(self, data=None, version=0):
        self.eventFlags = None
        self.keyCode = 0
        self.actions = []
        if not data is None:
            self.parse(data, version)

    def parse(self, data, version):
        self.actions = []
        self.eventFlags = data.readCLIPEVENTFLAGS(version)
        data.readUI32() # actionRecordSize, not needed here
        if self.eventFlags.keyPressEvent:
            self.keyCode = data.readUI8()
        action = data.readACTIONRECORD()
        while not action is None:
            self.actions.append(action)
            action = data.readACTIONRECORD()

    def __str__(self):
        return "[SWFClipActionRecord]"
                           
class SWFClipEventFlags(object):
    keyUpEvent = False
    keyDownEvent = False
    mouseUpEvent = False
    mouseDownEvent = False
    mouseMoveEvent = False
    unloadEvent = False
    enterFrameEvent = False
    loadEvent = False
    dragOverEvent = False # SWF6
    rollOutEvent = False # SWF6
    rollOverEvent = False # SWF6
    releaseOutsideEvent = False # SWF6
    releaseEvent = False # SWF6
    pressEvent = False # SWF6
    initializeEvent = False # SWF6
    dataEvent = False
    constructEvent = False # SWF7
    keyPressEvent = False # SWF6
    dragOutEvent = False # SWF6
    
    def __init__(self, data=None, version=0):
        if not data is None:
            self.parse(data, version)
            
    def parse(self, data, version):
        flags1 = data.readUI8();
        self.keyUpEvent = ((flags1 & 0x80) != 0)
        self.keyDownEvent = ((flags1 & 0x40) != 0)
        self.mouseUpEvent = ((flags1 & 0x20) != 0)
        self.mouseDownEvent = ((flags1 & 0x10) != 0)
        self.mouseMoveEvent = ((flags1 & 0x08) != 0)
        self.unloadEvent = ((flags1 & 0x04) != 0)
        self.enterFrameEvent = ((flags1 & 0x02) != 0)
        self.loadEvent = ((flags1 & 0x01) != 0)
        flags2 = data.readUI8()
        self.dragOverEvent = ((flags2 & 0x80) != 0)
        self.rollOutEvent = ((flags2 & 0x40) != 0)
        self.rollOverEvent = ((flags2 & 0x20) != 0)
        self.releaseOutsideEvent = ((flags2 & 0x10) != 0)
        self.releaseEvent = ((flags2 & 0x08) != 0)
        self.pressEvent = ((flags2 & 0x04) != 0)
        self.initializeEvent = ((flags2 & 0x02) != 0)
        self.dataEvent = ((flags2 & 0x01) != 0)
        if version >= 6:
            flags3 = data.readUI8()
            self.constructEvent = ((flags3 & 0x04) != 0)
            self.keyPressEvent = ((flags3 & 0x02) != 0)
            self.dragOutEvent = ((flags3 & 0x01) != 0)
            data.readUI8() # reserved, always 0
    
    def __str__(self):
        return "[SWFClipEventFlags]"
                       
class SWFZoneData(object):
    def __init__(self, data=None):
        if not data is None:
            self.parse(data)

    def parse(self, data):
        self.alignmentCoordinate = data.readFLOAT16()
        self.zoneRange = data.readFLOAT16()

    def __str__(self):
        return "[SWFZoneData]"
                                 
class SWFZoneRecord(object):
    def __init__(self, data=None):
        if not data is None:
            self.parse(data)

    def parse(self, data):
        self.zoneData = []
        numZoneData = data.readUI8()
        for i in range(0, numZoneData):
            self.zoneData.append(data.readZONEDATA())
        mask = data.readUI8()
        self.maskX = ((mask & 0x01) != 0)
        self.maskY = ((mask & 0x02) != 0)

    def __str__(self):
        return "[SWFZoneRecord]"
                    
