/* ------------------------------------------------------------
name: "fx_match_eq"
Code generated with Faust 2.70.3 (https://faust.grame.fr)
Compilation options: -lang cpp -ct 1 -cn FxMatchEq -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0
------------------------------------------------------------ */

#ifndef  __FxMatchEq_H__
#define  __FxMatchEq_H__

#ifndef FAUSTFLOAT
#define FAUSTFLOAT float
#endif 

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <math.h>

#ifndef FAUSTCLASS 
#define FAUSTCLASS FxMatchEq
#endif

#ifdef __APPLE__ 
#define exp10f __exp10f
#define exp10 __exp10
#endif

#if defined(_WIN32)
#define RESTRICT __restrict
#else
#define RESTRICT __restrict__
#endif

static float FxMatchEq_faustpower2_f(float value) {
	return value * value;
}

class FxMatchEq : public dsp {
	
 private:
	
	FAUSTFLOAT fHslider0;
	int fSampleRate;
	float fConst1;
	float fConst3;
	float fConst4;
	FAUSTFLOAT fHslider1;
	float fConst5;
	float fConst7;
	float fConst8;
	FAUSTFLOAT fHslider2;
	float fConst9;
	float fConst11;
	float fConst12;
	FAUSTFLOAT fHslider3;
	float fConst13;
	float fConst15;
	float fConst16;
	FAUSTFLOAT fHslider4;
	float fConst17;
	float fConst19;
	float fConst20;
	FAUSTFLOAT fHslider5;
	float fConst21;
	float fConst23;
	float fConst24;
	FAUSTFLOAT fHslider6;
	float fConst25;
	float fConst27;
	float fConst28;
	FAUSTFLOAT fHslider7;
	float fConst29;
	float fConst31;
	float fConst32;
	float fRec7[3];
	float fRec6[3];
	float fRec5[3];
	float fRec4[3];
	float fRec3[3];
	float fRec2[3];
	float fRec1[3];
	float fRec0[3];
	float fRec15[3];
	float fRec14[3];
	float fRec13[3];
	float fRec12[3];
	float fRec11[3];
	float fRec10[3];
	float fRec9[3];
	float fRec8[3];
	
 public:
	FxMatchEq() {}

	void metadata(Meta* m) { 
		m->declare("basics.lib/name", "Faust Basic Element Library");
		m->declare("basics.lib/tabulateNd", "Copyright (C) 2023 Bart Brouns <bart@magnetophon.nl>");
		m->declare("basics.lib/version", "1.12.0");
		m->declare("compile_options", "-lang cpp -ct 1 -cn FxMatchEq -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0");
		m->declare("filename", "fx_match_eq.dsp");
		m->declare("filters.lib/fir:author", "Julius O. Smith III");
		m->declare("filters.lib/fir:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/fir:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/iir:author", "Julius O. Smith III");
		m->declare("filters.lib/iir:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/iir:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/lowpass0_highpass1", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/name", "Faust Filters Library");
		m->declare("filters.lib/peak_eq:author", "Julius O. Smith III");
		m->declare("filters.lib/peak_eq:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/peak_eq:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/tf2:author", "Julius O. Smith III");
		m->declare("filters.lib/tf2:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/tf2:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/tf2s:author", "Julius O. Smith III");
		m->declare("filters.lib/tf2s:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/tf2s:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/version", "1.3.0");
		m->declare("maths.lib/author", "GRAME");
		m->declare("maths.lib/copyright", "GRAME");
		m->declare("maths.lib/license", "LGPL with exception");
		m->declare("maths.lib/name", "Faust Math Library");
		m->declare("maths.lib/version", "2.7.0");
		m->declare("name", "fx_match_eq");
		m->declare("platform.lib/name", "Generic Platform Library");
		m->declare("platform.lib/version", "1.3.0");
	}

	virtual int getNumInputs() {
		return 2;
	}
	virtual int getNumOutputs() {
		return 2;
	}
	
	static void classInit(int sample_rate) {
	}
	
	virtual void instanceConstants(int sample_rate) {
		fSampleRate = sample_rate;
		float fConst0 = std::min<float>(1.92e+05f, std::max<float>(1.0f, float(fSampleRate)));
		fConst1 = 25038.494f / (fConst0 * std::sin(70824.06f / fConst0));
		float fConst2 = std::tan(35412.03f / fConst0);
		fConst3 = 1.0f / fConst2;
		fConst4 = 2.0f * (1.0f - 1.0f / FxMatchEq_faustpower2_f(fConst2));
		fConst5 = 12459.557f / (fConst0 * std::sin(35242.387f / fConst0));
		float fConst6 = std::tan(17621.193f / fConst0);
		fConst7 = 1.0f / fConst6;
		fConst8 = 2.0f * (1.0f - 1.0f / FxMatchEq_faustpower2_f(fConst6));
		fConst9 = 6198.3623f / (fConst0 * std::sin(17530.088f / fConst0));
		float fConst10 = std::tan(8765.044f / fConst0);
		fConst11 = 1.0f / fConst10;
		fConst12 = 2.0f * (1.0f - 1.0f / FxMatchEq_faustpower2_f(fConst10));
		fConst13 = 3085.044f / (fConst0 * std::sin(8727.345f / fConst0));
		float fConst14 = std::tan(4363.6724f / fConst0);
		fConst15 = 1.0f / fConst14;
		fConst16 = 2.0f * (1.0f - 1.0f / FxMatchEq_faustpower2_f(fConst14));
		fConst17 = 1536.2388f / (fConst0 * std::sin(4341.681f / fConst0));
		float fConst18 = std::tan(2170.8406f / fConst0);
		fConst19 = 1.0f / fConst18;
		fConst20 = 2.0f * (1.0f - 1.0f / FxMatchEq_faustpower2_f(fConst18));
		fConst21 = 763.40704f / (fConst0 * std::sin(2161.4158f / fConst0));
		float fConst22 = std::tan(1080.7079f / fConst0);
		fConst23 = 1.0f / fConst22;
		fConst24 = 2.0f * (1.0f - 1.0f / FxMatchEq_faustpower2_f(fConst22));
		fConst25 = 380.13272f / (fConst0 * std::sin(1074.4247f / fConst0));
		float fConst26 = std::tan(537.21234f / fConst0);
		fConst27 = 1.0f / fConst26;
		fConst28 = 2.0f * (1.0f - 1.0f / FxMatchEq_faustpower2_f(fConst26));
		fConst29 = 188.49556f / (fConst0 * std::sin(534.07074f / fConst0));
		float fConst30 = std::tan(267.03537f / fConst0);
		fConst31 = 1.0f / fConst30;
		fConst32 = 2.0f * (1.0f - 1.0f / FxMatchEq_faustpower2_f(fConst30));
	}
	
	virtual void instanceResetUserInterface() {
		fHslider0 = FAUSTFLOAT(0.0f);
		fHslider1 = FAUSTFLOAT(0.0f);
		fHslider2 = FAUSTFLOAT(0.0f);
		fHslider3 = FAUSTFLOAT(0.0f);
		fHslider4 = FAUSTFLOAT(0.0f);
		fHslider5 = FAUSTFLOAT(0.0f);
		fHslider6 = FAUSTFLOAT(0.0f);
		fHslider7 = FAUSTFLOAT(0.0f);
	}
	
	virtual void instanceClear() {
		for (int l0 = 0; l0 < 3; l0 = l0 + 1) {
			fRec7[l0] = 0.0f;
		}
		for (int l1 = 0; l1 < 3; l1 = l1 + 1) {
			fRec6[l1] = 0.0f;
		}
		for (int l2 = 0; l2 < 3; l2 = l2 + 1) {
			fRec5[l2] = 0.0f;
		}
		for (int l3 = 0; l3 < 3; l3 = l3 + 1) {
			fRec4[l3] = 0.0f;
		}
		for (int l4 = 0; l4 < 3; l4 = l4 + 1) {
			fRec3[l4] = 0.0f;
		}
		for (int l5 = 0; l5 < 3; l5 = l5 + 1) {
			fRec2[l5] = 0.0f;
		}
		for (int l6 = 0; l6 < 3; l6 = l6 + 1) {
			fRec1[l6] = 0.0f;
		}
		for (int l7 = 0; l7 < 3; l7 = l7 + 1) {
			fRec0[l7] = 0.0f;
		}
		for (int l8 = 0; l8 < 3; l8 = l8 + 1) {
			fRec15[l8] = 0.0f;
		}
		for (int l9 = 0; l9 < 3; l9 = l9 + 1) {
			fRec14[l9] = 0.0f;
		}
		for (int l10 = 0; l10 < 3; l10 = l10 + 1) {
			fRec13[l10] = 0.0f;
		}
		for (int l11 = 0; l11 < 3; l11 = l11 + 1) {
			fRec12[l11] = 0.0f;
		}
		for (int l12 = 0; l12 < 3; l12 = l12 + 1) {
			fRec11[l12] = 0.0f;
		}
		for (int l13 = 0; l13 < 3; l13 = l13 + 1) {
			fRec10[l13] = 0.0f;
		}
		for (int l14 = 0; l14 < 3; l14 = l14 + 1) {
			fRec9[l14] = 0.0f;
		}
		for (int l15 = 0; l15 < 3; l15 = l15 + 1) {
			fRec8[l15] = 0.0f;
		}
	}
	
	virtual void init(int sample_rate) {
		classInit(sample_rate);
		instanceInit(sample_rate);
	}
	
	virtual void instanceInit(int sample_rate) {
		instanceConstants(sample_rate);
		instanceResetUserInterface();
		instanceClear();
	}
	
	virtual FxMatchEq* clone() {
		return new FxMatchEq();
	}
	
	virtual int getSampleRate() {
		return fSampleRate;
	}
	
	virtual void buildUserInterface(UI* ui_interface) {
		ui_interface->openVerticalBox("fx_match_eq");
		ui_interface->addHorizontalSlider("g11272", &fHslider0, FAUSTFLOAT(0.0f), FAUSTFLOAT(-9.0f), FAUSTFLOAT(9.0f), FAUSTFLOAT(0.1f));
		ui_interface->addHorizontalSlider("g1389", &fHslider3, FAUSTFLOAT(0.0f), FAUSTFLOAT(-9.0f), FAUSTFLOAT(9.0f), FAUSTFLOAT(0.1f));
		ui_interface->addHorizontalSlider("g171", &fHslider6, FAUSTFLOAT(0.0f), FAUSTFLOAT(-9.0f), FAUSTFLOAT(9.0f), FAUSTFLOAT(0.1f));
		ui_interface->addHorizontalSlider("g2790", &fHslider2, FAUSTFLOAT(0.0f), FAUSTFLOAT(-9.0f), FAUSTFLOAT(9.0f), FAUSTFLOAT(0.1f));
		ui_interface->addHorizontalSlider("g344", &fHslider5, FAUSTFLOAT(0.0f), FAUSTFLOAT(-9.0f), FAUSTFLOAT(9.0f), FAUSTFLOAT(0.1f));
		ui_interface->addHorizontalSlider("g5609", &fHslider1, FAUSTFLOAT(0.0f), FAUSTFLOAT(-9.0f), FAUSTFLOAT(9.0f), FAUSTFLOAT(0.1f));
		ui_interface->addHorizontalSlider("g691", &fHslider4, FAUSTFLOAT(0.0f), FAUSTFLOAT(-9.0f), FAUSTFLOAT(9.0f), FAUSTFLOAT(0.1f));
		ui_interface->addHorizontalSlider("g85", &fHslider7, FAUSTFLOAT(0.0f), FAUSTFLOAT(-9.0f), FAUSTFLOAT(9.0f), FAUSTFLOAT(0.1f));
		ui_interface->closeBox();
	}
	
	virtual void compute(int count, FAUSTFLOAT** RESTRICT inputs, FAUSTFLOAT** RESTRICT outputs) {
		FAUSTFLOAT* input0 = inputs[0];
		FAUSTFLOAT* input1 = inputs[1];
		FAUSTFLOAT* output0 = outputs[0];
		FAUSTFLOAT* output1 = outputs[1];
		float fSlow0 = float(fHslider0);
		int iSlow1 = fSlow0 > 0.0f;
		float fSlow2 = fConst1 * std::pow(1e+01f, 0.05f * std::fabs(fSlow0));
		float fSlow3 = ((iSlow1) ? fConst1 : fSlow2);
		float fSlow4 = fConst3 * (fConst3 + fSlow3) + 1.0f;
		float fSlow5 = ((iSlow1) ? fSlow2 : fConst1);
		float fSlow6 = fConst3 * (fConst3 - fSlow5) + 1.0f;
		float fSlow7 = fConst3 * (fConst3 - fSlow3) + 1.0f;
		float fSlow8 = float(fHslider1);
		int iSlow9 = fSlow8 > 0.0f;
		float fSlow10 = fConst5 * std::pow(1e+01f, 0.05f * std::fabs(fSlow8));
		float fSlow11 = ((iSlow9) ? fConst5 : fSlow10);
		float fSlow12 = fConst7 * (fConst7 + fSlow11) + 1.0f;
		float fSlow13 = ((iSlow9) ? fSlow10 : fConst5);
		float fSlow14 = fConst7 * (fConst7 - fSlow13) + 1.0f;
		float fSlow15 = fConst7 * (fConst7 - fSlow11) + 1.0f;
		float fSlow16 = float(fHslider2);
		int iSlow17 = fSlow16 > 0.0f;
		float fSlow18 = fConst9 * std::pow(1e+01f, 0.05f * std::fabs(fSlow16));
		float fSlow19 = ((iSlow17) ? fConst9 : fSlow18);
		float fSlow20 = fConst11 * (fConst11 + fSlow19) + 1.0f;
		float fSlow21 = ((iSlow17) ? fSlow18 : fConst9);
		float fSlow22 = fConst11 * (fConst11 - fSlow21) + 1.0f;
		float fSlow23 = fConst11 * (fConst11 - fSlow19) + 1.0f;
		float fSlow24 = float(fHslider3);
		int iSlow25 = fSlow24 > 0.0f;
		float fSlow26 = fConst13 * std::pow(1e+01f, 0.05f * std::fabs(fSlow24));
		float fSlow27 = ((iSlow25) ? fConst13 : fSlow26);
		float fSlow28 = fConst15 * (fConst15 + fSlow27) + 1.0f;
		float fSlow29 = ((iSlow25) ? fSlow26 : fConst13);
		float fSlow30 = fConst15 * (fConst15 - fSlow29) + 1.0f;
		float fSlow31 = fConst15 * (fConst15 - fSlow27) + 1.0f;
		float fSlow32 = float(fHslider4);
		int iSlow33 = fSlow32 > 0.0f;
		float fSlow34 = fConst17 * std::pow(1e+01f, 0.05f * std::fabs(fSlow32));
		float fSlow35 = ((iSlow33) ? fConst17 : fSlow34);
		float fSlow36 = fConst19 * (fConst19 + fSlow35) + 1.0f;
		float fSlow37 = ((iSlow33) ? fSlow34 : fConst17);
		float fSlow38 = fConst19 * (fConst19 - fSlow37) + 1.0f;
		float fSlow39 = fConst19 * (fConst19 - fSlow35) + 1.0f;
		float fSlow40 = float(fHslider5);
		int iSlow41 = fSlow40 > 0.0f;
		float fSlow42 = fConst21 * std::pow(1e+01f, 0.05f * std::fabs(fSlow40));
		float fSlow43 = ((iSlow41) ? fConst21 : fSlow42);
		float fSlow44 = fConst23 * (fConst23 + fSlow43) + 1.0f;
		float fSlow45 = ((iSlow41) ? fSlow42 : fConst21);
		float fSlow46 = fConst23 * (fConst23 - fSlow45) + 1.0f;
		float fSlow47 = fConst23 * (fConst23 - fSlow43) + 1.0f;
		float fSlow48 = float(fHslider6);
		int iSlow49 = fSlow48 > 0.0f;
		float fSlow50 = fConst25 * std::pow(1e+01f, 0.05f * std::fabs(fSlow48));
		float fSlow51 = ((iSlow49) ? fConst25 : fSlow50);
		float fSlow52 = fConst27 * (fConst27 + fSlow51) + 1.0f;
		float fSlow53 = ((iSlow49) ? fSlow50 : fConst25);
		float fSlow54 = fConst27 * (fConst27 - fSlow53) + 1.0f;
		float fSlow55 = fConst27 * (fConst27 - fSlow51) + 1.0f;
		float fSlow56 = float(fHslider7);
		int iSlow57 = fSlow56 > 0.0f;
		float fSlow58 = fConst29 * std::pow(1e+01f, 0.05f * std::fabs(fSlow56));
		float fSlow59 = ((iSlow57) ? fConst29 : fSlow58);
		float fSlow60 = fConst31 * (fConst31 + fSlow59) + 1.0f;
		float fSlow61 = ((iSlow57) ? fSlow58 : fConst29);
		float fSlow62 = fConst31 * (fConst31 - fSlow61) + 1.0f;
		float fSlow63 = fConst31 * (fConst31 - fSlow59) + 1.0f;
		float fSlow64 = fConst31 * (fConst31 + fSlow61) + 1.0f;
		float fSlow65 = fConst27 * (fConst27 + fSlow53) + 1.0f;
		float fSlow66 = fConst23 * (fConst23 + fSlow45) + 1.0f;
		float fSlow67 = fConst19 * (fConst19 + fSlow37) + 1.0f;
		float fSlow68 = fConst15 * (fConst15 + fSlow29) + 1.0f;
		float fSlow69 = fConst11 * (fConst11 + fSlow21) + 1.0f;
		float fSlow70 = fConst7 * (fConst7 + fSlow13) + 1.0f;
		float fSlow71 = fConst3 * (fConst3 + fSlow5) + 1.0f;
		for (int i0 = 0; i0 < count; i0 = i0 + 1) {
			float fTemp0 = fConst4 * fRec0[1];
			float fTemp1 = fConst8 * fRec1[1];
			float fTemp2 = fConst12 * fRec2[1];
			float fTemp3 = fConst16 * fRec3[1];
			float fTemp4 = fConst20 * fRec4[1];
			float fTemp5 = fConst24 * fRec5[1];
			float fTemp6 = fConst28 * fRec6[1];
			float fTemp7 = fConst32 * fRec7[1];
			fRec7[0] = float(input0[i0]) - (fRec7[2] * fSlow63 + fTemp7) / fSlow60;
			fRec6[0] = (fTemp7 + fRec7[0] * fSlow64 + fRec7[2] * fSlow62) / fSlow60 - (fRec6[2] * fSlow55 + fTemp6) / fSlow52;
			fRec5[0] = (fTemp6 + fRec6[0] * fSlow65 + fRec6[2] * fSlow54) / fSlow52 - (fRec5[2] * fSlow47 + fTemp5) / fSlow44;
			fRec4[0] = (fTemp5 + fRec5[0] * fSlow66 + fRec5[2] * fSlow46) / fSlow44 - (fRec4[2] * fSlow39 + fTemp4) / fSlow36;
			fRec3[0] = (fTemp4 + fRec4[0] * fSlow67 + fRec4[2] * fSlow38) / fSlow36 - (fRec3[2] * fSlow31 + fTemp3) / fSlow28;
			fRec2[0] = (fTemp3 + fRec3[0] * fSlow68 + fRec3[2] * fSlow30) / fSlow28 - (fRec2[2] * fSlow23 + fTemp2) / fSlow20;
			fRec1[0] = (fTemp2 + fRec2[0] * fSlow69 + fRec2[2] * fSlow22) / fSlow20 - (fRec1[2] * fSlow15 + fTemp1) / fSlow12;
			fRec0[0] = (fTemp1 + fRec1[0] * fSlow70 + fRec1[2] * fSlow14) / fSlow12 - (fRec0[2] * fSlow7 + fTemp0) / fSlow4;
			output0[i0] = FAUSTFLOAT((fTemp0 + fRec0[0] * fSlow71 + fRec0[2] * fSlow6) / fSlow4);
			float fTemp8 = fConst4 * fRec8[1];
			float fTemp9 = fConst8 * fRec9[1];
			float fTemp10 = fConst12 * fRec10[1];
			float fTemp11 = fConst16 * fRec11[1];
			float fTemp12 = fConst20 * fRec12[1];
			float fTemp13 = fConst24 * fRec13[1];
			float fTemp14 = fConst28 * fRec14[1];
			float fTemp15 = fConst32 * fRec15[1];
			fRec15[0] = float(input1[i0]) - (fSlow63 * fRec15[2] + fTemp15) / fSlow60;
			fRec14[0] = (fTemp15 + fRec15[0] * fSlow64 + fSlow62 * fRec15[2]) / fSlow60 - (fSlow55 * fRec14[2] + fTemp14) / fSlow52;
			fRec13[0] = (fTemp14 + fRec14[0] * fSlow65 + fSlow54 * fRec14[2]) / fSlow52 - (fSlow47 * fRec13[2] + fTemp13) / fSlow44;
			fRec12[0] = (fTemp13 + fRec13[0] * fSlow66 + fSlow46 * fRec13[2]) / fSlow44 - (fSlow39 * fRec12[2] + fTemp12) / fSlow36;
			fRec11[0] = (fTemp12 + fRec12[0] * fSlow67 + fSlow38 * fRec12[2]) / fSlow36 - (fSlow31 * fRec11[2] + fTemp11) / fSlow28;
			fRec10[0] = (fTemp11 + fRec11[0] * fSlow68 + fSlow30 * fRec11[2]) / fSlow28 - (fSlow23 * fRec10[2] + fTemp10) / fSlow20;
			fRec9[0] = (fTemp10 + fRec10[0] * fSlow69 + fSlow22 * fRec10[2]) / fSlow20 - (fSlow15 * fRec9[2] + fTemp9) / fSlow12;
			fRec8[0] = (fTemp9 + fRec9[0] * fSlow70 + fSlow14 * fRec9[2]) / fSlow12 - (fSlow7 * fRec8[2] + fTemp8) / fSlow4;
			output1[i0] = FAUSTFLOAT((fTemp8 + fRec8[0] * fSlow71 + fSlow6 * fRec8[2]) / fSlow4);
			fRec7[2] = fRec7[1];
			fRec7[1] = fRec7[0];
			fRec6[2] = fRec6[1];
			fRec6[1] = fRec6[0];
			fRec5[2] = fRec5[1];
			fRec5[1] = fRec5[0];
			fRec4[2] = fRec4[1];
			fRec4[1] = fRec4[0];
			fRec3[2] = fRec3[1];
			fRec3[1] = fRec3[0];
			fRec2[2] = fRec2[1];
			fRec2[1] = fRec2[0];
			fRec1[2] = fRec1[1];
			fRec1[1] = fRec1[0];
			fRec0[2] = fRec0[1];
			fRec0[1] = fRec0[0];
			fRec15[2] = fRec15[1];
			fRec15[1] = fRec15[0];
			fRec14[2] = fRec14[1];
			fRec14[1] = fRec14[0];
			fRec13[2] = fRec13[1];
			fRec13[1] = fRec13[0];
			fRec12[2] = fRec12[1];
			fRec12[1] = fRec12[0];
			fRec11[2] = fRec11[1];
			fRec11[1] = fRec11[0];
			fRec10[2] = fRec10[1];
			fRec10[1] = fRec10[0];
			fRec9[2] = fRec9[1];
			fRec9[1] = fRec9[0];
			fRec8[2] = fRec8[1];
			fRec8[1] = fRec8[0];
		}
	}

};

#endif
